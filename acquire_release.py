import os
import pynvml
import random
import time
import sys
from signal import SIGTERM

    
shared_folder_path = "/root/Dev/shared"  # Adjust this path

def acquire_gpu_lock(gpu_id, max_allocations_per_gpu):
    for i in range(max_allocations_per_gpu):
        lock_file = os.path.join(shared_folder_path, f"gpu_{gpu_id}_{i}.lock")
        #print("Lock in acquire_gpu_lock ",f"gpu_{gpu_id}_{i}.lock")
        try:
            fd = os.open(lock_file, os.O_CREAT | os.O_EXCL | os.O_RDWR)
            os.close(fd)
            print("Lock Created with ", f"gpu_{gpu_id}_{i}.lock")
            print("*******************************************************")
            return i
        except FileExistsError:
            #print("exception in acquire_gpu_lock")
            continue  # This slot is already taken, try the next one
    # All slots are taken
    return -1
    


def release_gpu_lock(gpu_id, index):
    # Attempt to find and remove any lock file for the GPU
    #print("index:",index)
    #print("gpu_id:",gpu_id)
    lock_files = [f for f in os.listdir(shared_folder_path) if f.startswith(f"gpu_{gpu_id}_")]
    if not lock_files:
        return  # No lock files found for this GPU
        
    #print("Lock in release_gpu_lock ",f"gpu_{gpu_id}_{index}.lock")

    user_lock_file = os.path.join(shared_folder_path, f"gpu_{gpu_id}_{index}.lock") #os.path.join(shared_folder_path, sorted(lock_files)[0])
    try:
        os.remove(user_lock_file)
        print("Lock deleted ",f"gpu_{gpu_id}_{index}.lock")
        print("*******************************************************")
    except FileNotFoundError:
        print("Delete not done correctly")
        pass


# Your acquire_gpu_lock function goes here if not already defined

def get_gpu(required_memory_gb=None, operational_gpus=None, max_allocations_per_gpu=None):
    if required_memory_gb is None:
        required_memory_gb = 5  # Default value if not provided
    if operational_gpus is None:
        operational_gpus = [0,1,2,4]  # Default value if not provided
    if max_allocations_per_gpu is None:
        max_allocations_per_gpu = 6
    pynvml.nvmlInit()
    print_message_once = True
    while True:
        random.shuffle(operational_gpus)  # Randomize GPU order
        for i in operational_gpus:
            handle = pynvml.nvmlDeviceGetHandleByIndex(i)
            info = pynvml.nvmlDeviceGetMemoryInfo(handle)
            available_memory_gb = (info.total - info.used) / 1024**3
            if print_message_once:
                print(f"GPU {i}: Available Memory: {available_memory_gb} GB")
            else:
                print("wait...", end="", flush=True)  # Print a wait... without newline
            acquired_gpu_index = acquire_gpu_lock(i, max_allocations_per_gpu)
            if available_memory_gb >= required_memory_gb and acquired_gpu_index in range(max_allocations_per_gpu):
                # If enough memory is available and GPU is successfully locked, return GPU ID and memory used
                print(f"Acquired GPU is {i}")
                return i, 40 - available_memory_gb, acquired_gpu_index   # Assuming 40GB total memory per GPU
            else:
                if print_message_once:
                    release_gpu_lock(i, acquired_gpu_index)
                    print(" The GPU memory is currently unavailable, or the number of users has reached the limit on the GPU ")
                    print_message_once = False
                else:
                    release_gpu_lock(i, acquired_gpu_index)
                    

        # If no valid GPU found in the current iteration, retry the loop after a delay
        time.sleep(20)  # Changed the delay to 20 seconds
    pynvml.nvmlShutdown()


def get_gpu_for_llm(required_memory_gb=None, operational_gpus=None, max_allocations_per_gpu=None):
    if required_memory_gb is None:
        required_memory_gb = 26  # Default value if not provided
    if operational_gpus is None:
        operational_gpus = [0,1,2,4]  # Default value if not provided
    if max_allocations_per_gpu is None:
        max_allocations_per_gpu = 1
    pynvml.nvmlInit()
    print_message_once = True
    while True:
        random.shuffle(operational_gpus)  # Randomize GPU order
        for i in operational_gpus:
            handle = pynvml.nvmlDeviceGetHandleByIndex(i)
            info = pynvml.nvmlDeviceGetMemoryInfo(handle)
            available_memory_gb = (info.total - info.used) / 1024**3
            if print_message_once:
                print(f"GPU {i}: Available Memory: {available_memory_gb} GB")
            else:
                print("wait...", end="", flush=True)  # Print a wait... without newline
            acquired_gpu_index = acquire_gpu_lock(i, max_allocations_per_gpu)
            if available_memory_gb >= required_memory_gb and acquired_gpu_index in range(max_allocations_per_gpu):
                # If enough memory is available and GPU is successfully locked, return GPU ID and memory used
                print(f"Acquired GPU is {i}")
                return i, 40 - available_memory_gb, acquired_gpu_index   # Assuming 40GB total memory per GPU
            else:
                if print_message_once:
                    if acquired_gpu_index in range(max_allocations_per_gpu):
                    	release_gpu_lock(i, acquired_gpu_index)
                    print(" The GPU memory is currently unavailable, or the number of users has reached the limit on the GPU ")
                    print_message_once = False
                else:
                    if acquired_gpu_index in range(max_allocations_per_gpu):
                    	release_gpu_lock(i, acquired_gpu_index)
                    

        # If no valid GPU found in the current iteration, retry the loop after a delay
        time.sleep(20)  # Changed the delay to 20 seconds
    pynvml.nvmlShutdown()

def get_gpu_pool(required_memory_gb=None, max_allocations_per_gpu=None):
    if required_memory_gb is None:
        required_memory_gb = 1  # Default value if not provided
    if max_allocations_per_gpu is None:
        max_allocations_per_gpu = 40
    pynvml.nvmlInit()
    print_message_once = True
    while True:
        gpu_pair = random.choice([[0,1],[2,4]])  # Choose either [0, 1] or [2, 3]
        acquired_gpu_indexes = []

        # Check both GPUs in the pair before attempting to acquire locks
        gpu_pair_valid = all(
            40-((pynvml.nvmlDeviceGetMemoryInfo(pynvml.nvmlDeviceGetHandleByIndex(gpu)).used)/ 1024**3) >=
            required_memory_gb
            for gpu in gpu_pair
        )

       
        if gpu_pair_valid:
            # Attempt to acquire locks for both GPUs in the pair
            for gpu in gpu_pair:
                handle = pynvml.nvmlDeviceGetHandleByIndex(gpu)
                info = pynvml.nvmlDeviceGetMemoryInfo(handle)
                available_memory_gb = (info.total - info.used) / 1024**3

                if print_message_once:
                    print(f"Acquired GPU {gpu}: Available Memory: {available_memory_gb} GB")
                else:
                    print("wait...", end="", flush=True)  # Print a wait... without newline

                acquired_gpu_index = acquire_gpu_lock(gpu, max_allocations_per_gpu)
                #print("acquired_gpu_index: ",acquired_gpu_index)
                
                if available_memory_gb >= required_memory_gb and acquired_gpu_index in range(max_allocations_per_gpu):
                    acquired_gpu_indexes.append((gpu, acquired_gpu_index))
                else:
                    # If the lock cannot be acquired, release any previously acquired locks and break out of the loop
                    if acquired_gpu_index == -1:
                        print("All GPUs are being used, please wait!")
                        for gpu_id, index in acquired_gpu_indexes:
                            release_gpu_lock(gpu_id, index)
                            acquired_gpu_indexes = []
                    else:
                    # If the lock cannot be acquired, release any previously acquired locks and break out of the loop
                        for gpu_id, index in acquired_gpu_indexes:
                            release_gpu_lock(gpu_id, index)
                            acquired_gpu_indexes = []
                    break
            #print("len(acquired_gpu_indexes): ",len(acquired_gpu_indexes))
            #print("len(gpu_pair): ", len(gpu_pair))
            if len(acquired_gpu_indexes) == len(gpu_pair):
                # If locks are acquired for both GPUs, return GPU IDs and memory used
                gpu_ids, indexes = zip(*acquired_gpu_indexes)
                return gpu_ids, 40 - available_memory_gb, acquired_gpu_indexes

        else:
            if print_message_once:
                print(" The GPU memory is currently unavailable, or the number of users has reached the limit on the GPUs ")
                print_message_once = False
            else:
                print(" wait! ")

        # If no valid GPU pair found in the current iteration, retry the loop after a delay
        time.sleep(15)  # Changed the delay to 20 seconds

    pynvml.nvmlShutdown()


def release_gpu_memory():
    time.sleep(2)
    os.kill(os.getpid(), SIGTERM)
    



