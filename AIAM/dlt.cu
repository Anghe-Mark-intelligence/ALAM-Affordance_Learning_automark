//https://github.com/Anghe-Mark-intelligence/ALAM-Affordance_Learning_automark/tree/main
#include <iostream>
#include <cmath>
#include <cuda_runtime.h>

#define CHECK_CUDA_ERROR(err) { \
    if (err != cudaSuccess) { \
        std::cerr << "CUDA Error: " << cudaGetErrorString(err) << std::endl; \
        exit(-1); \
    } \
}

// GPU Kernel function: Forward pass
__global__ void forward_pass(float *input, float *weights, float *output, int num_input, int num_output) {
    int idx = blockIdx.x * blockDim.x + threadIdx.x;
    if (idx < num_output) {
        output[idx] = 0;
        // Compute output for the current neuron
        for (int i = 0; i < num_input; i++) {
            output[idx] += input[i] * weights[i * num_output + idx];
        }
    }
}

// GPU Kernel function: Backward pass
__global__ void backward_pass(float *input, float *weights, float *output, float *grad_input, float *grad_weights, int num_input, int num_output) {
    int idx = blockIdx.x * blockDim.x + threadIdx.x;
    if (idx < num_input) {
        grad_input[idx] = 0;
        // Compute gradients for input layer
        for (int i = 0; i < num_output; i++) {
            grad_input[idx] += output[i] * weights[idx * num_output + i];
        }
    }
    
    if (idx < num_output) {
        // Compute gradients for weights
        for (int i = 0; i < num_input; i++) {
            grad_weights[i * num_output + idx] = input[i] * output[idx];
        }
    }
}

// Main function
int main() {
    const int num_input = 4;  // Number of input neurons
    const int num_output = 3; // Number of output neurons
    float input[num_input] = {1.0f, 2.0f, 3.0f, 4.0f}; // Input data
    float weights[num_input * num_output] = {0.5f, -0.2f, 0.3f, 0.1f, -0.4f, 0.8f, -0.3f, 0.2f, 0.6f, 0.5f, -0.1f, 0.4f}; // Weights

    float *d_input, *d_weights, *d_output, *d_grad_input, *d_grad_weights;
    float output[num_output];

    cudaError_t err;

    // Allocate memory on GPU
    err = cudaMalloc((void**)&d_input, num_input * sizeof(float));
    CHECK_CUDA_ERROR(err);
    err = cudaMalloc((void**)&d_weights, num_input * num_output * sizeof(float));
    CHECK_CUDA_ERROR(err);
    err = cudaMalloc((void**)&d_output, num_output * sizeof(float));
    CHECK_CUDA_ERROR(err);
    err = cudaMalloc((void**)&d_grad_input, num_input * sizeof(float));
    CHECK_CUDA_ERROR(err);
    err = cudaMalloc((void**)&d_grad_weights, num_input * num_output * sizeof(float));
    CHECK_CUDA_ERROR(err);

    // Copy input data and weights from host to device (GPU)
    err = cudaMemcpy(d_input, input, num_input * sizeof(float), cudaMemcpyHostToDevice);
    CHECK_CUDA_ERROR(err);
    err = cudaMemcpy(d_weights, weights, num_input * num_output * sizeof(float), cudaMemcpyHostToDevice);
    CHECK_CUDA_ERROR(err);

    // Set the number of threads and blocks for execution
    int blockSize = 256;
    int numBlocks = (num_output + blockSize - 1) / blockSize;

    // Execute forward pass on GPU
    forward_pass<<<numBlocks, blockSize>>>(d_input, d_weights, d_output, num_input, num_output);
    err = cudaGetLastError();
    CHECK_CUDA_ERROR(err);

    // Copy the output from device back to host
    err = cudaMemcpy(output, d_output, num_output * sizeof(float), cudaMemcpyDeviceToHost);
    CHECK_CUDA_ERROR(err);

    // Print the result of the forward pass
    std::cout << "Output of forward pass:\n";
    for (int i = 0; i < num_output; i++) {
        std::cout << "output[" << i << "] = " << output[i] << "\n";
    }

    // Execute backward pass on GPU (for gradient computation)
    backward_pass<<<numBlocks, blockSize>>>(d_input, d_weights, d_output, d_grad_input, d_grad_weights, num_input, num_output);
    err = cudaGetLastError();
    CHECK_CUDA_ERROR(err);

    // Clean up and free memory on GPU
    cudaFree(d_input);
    cudaFree(d_weights);
    cudaFree(d_output);
    cudaFree(d_grad_input);
    cudaFree(d_grad_weights);

    return 0;
}
