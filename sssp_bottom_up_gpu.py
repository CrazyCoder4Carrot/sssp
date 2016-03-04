import pycuda.autoinit
import pycuda.driver as drv
import numpy
from pycuda.autoinit import context
import graph
from pycuda.compiler import SourceModule
mod = SourceModule("""
#include<stdio.h>
typedef long index_t;
typedef long vertex_t;
typedef double path_t;
typedef long depth_t;
__global__ void traverse_one(index_t *dev_beg_pos, index_t *dev_csr,path_t *dev_weight,path_t *dev_sa_global, bool *dev_flag_traverse)
{
    __shared__ path_t dev_sa[218];
    int id = threadIdx.x + blockIdx.x * blockDim.x;
    const int INF = 0x7fffffff;
    dev_sa[id] = INF;
    if(id == 0)
    {
        dev_sa[0] = 0;
    }
    __syncthreads();
    while(*dev_flag_traverse)
    {
        if(id == 0)
        {
            *dev_flag_traverse = false;
        }
        __syncthreads();
        for(index_t j = dev_beg_pos[id]; j < dev_beg_pos[id+1]; j++)
        {
            if(dev_sa[dev_csr[j]] < INF)
            {
                if(dev_sa[id] > dev_sa[dev_csr[j]] + dev_weight[j])
                {
                    dev_sa[id] = dev_sa[dev_csr[j]] + dev_weight[j];
                    if(!(*dev_flag_traverse))
                    {
                        *dev_flag_traverse = true;
                    }
                }
            }
        }
        __syncthreads();
    }
    __syncthreads();
    dev_sa_global[id] = dev_sa[id];
    __syncthreads();
}
""")
def printresult(sa):
    file_result = "result.txt"
    res = open(file_result,"w")
    for value in sa:
        res.write(str(value)+"\n ")
    res.close()
def bfs_sa(root, g):
    v = g.vertex_count
    e = g.edge_count
    beg_pos = numpy.asarray(g.beg_pos, dtype = numpy.long)

    csr = numpy.asarray(g.csr, dtype = numpy.long)

    weight = numpy.asarray(g.weight, dtype = numpy.float64)

    sa = numpy.zeros(v, dtype = numpy.float64)

    flag_traverse = numpy.ones(1, dtype = numpy.bool)

    print "v=" +  str(v) + ", e=" + str(e)
    traverse_one = mod.get_function("traverse_one")
    traverse_one(drv.In(beg_pos), drv.In(csr) ,drv.In(weight), drv.Out(sa), drv.In(flag_traverse), block = (v,1,1))
    context.synchronize()
    print sa
    printresult(sa)
def main():
    beg_file = "/home/hadoop/dataset_sssp/beg.txt"
    csr_file = "/home/hadoop/dataset_sssp/csr.txt"
    weight_file = "/home/hadoop/dataset_sssp/weight.txt"
    g = graph.graph(beg_file, csr_file,weight_file)
    bfs_sa(0,g)
    return 0

if __name__ == '__main__':
    main()
