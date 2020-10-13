""" An interface for serializing and deserializing bittensor tensors"""
from bittensor import bittensor_pb2
from loguru import logger
import numpy as np
import pickle
import torch
from typing import List, Tuple, Dict, Optional

import bittensor
   
def torch_dtype_to_bittensor_dtype(tdtype):
    if tdtype == torch.float32:
        dtype = bittensor_pb2.DataType.FLOAT32
    elif tdtype == torch.float64:
        dtype = bittensor_pb2.DataType.FLOAT64
    elif tdtype == torch.int32:
        dtype = bittensor_pb2.DataType.INT32
    elif tdtype == torch.int64:
        dtype = bittensor_pb2.DataType.INT64
    else:
        dtype = bittensor_pb2.DataType.UNKNOWN
    return dtype


def bittensor_dtype_to_torch_dtype(odtype):
    if odtype == bittensor_pb2.DataType.FLOAT32:
        dtype = torch.float32
    elif odtype == bittensor_pb2.DataType.FLOAT64:
        dtype = torch.float64
    elif odtype == bittensor_pb2.DataType.INT32:
        dtype = torch.int32
    elif odtype == bittensor_pb2.DataType.INT64: 
        dtype = torch.int64
    else:
        # TODO (const): raise error
        dtype = torch.float32
    return dtype

def bittensor_dtype_np_dtype(odtype):
    if odtype == bittensor_pb2.DataType.FLOAT32:
        dtype = np.float32
    elif odtype == bittensor_pb2.DataType.FLOAT64:
        dtype = np.float64
    elif odtype == bittensor_pb2.DataType.INT32:
        dtype = np.int32
    elif odtype == bittensor_pb2.DataType.INT64: 
        dtype = np.int64
    else:
        # TODO(const): raise error.
        dtype = np.float32
    return dtype

class PyTorchSerializer():
    
    @staticmethod
    def deserialize(proto: bittensor_pb2.Tensor) -> object:
        """Deserializes an bittensor_pb2.Tensor to a torch.Tensor object.

        Args:
            proto (bittensor_pb2.Tensor): Proto to derserialize.

        Returns:
            List[object]:
        """
        # Check typing
        if proto.modality == bittensor_pb2.Modality.IMAGE:
            return PyTorchSerializer.deserialize_image( proto )
        
        elif proto.modality == bittensor_pb2.Modality.TEXT:
            return PyTorchSerializer.deserialize_text( proto )
        
        elif proto.modality == bittensor_pb2.Modality.TENSOR:
            return PyTorchSerializer.deserialize_tensor( proto )
        
        else:
            raise NotImplementedError
   
    @staticmethod
    def serialize(tensor: torch.Tensor, modality: bittensor_pb2.Modality) -> bittensor_pb2.Tensor:
        """Serializes a object with modality into a bittensor Tensor proto.

        Args:
            tensor (torch.Tensor): torch.Tensor object with modality TEXT, IMAGE, TENSOR

        Returns:
            bittensor_pb2.Tensor: Serialized tensor as bittensor_pb2.proto. 
        """
        # Check typing
        if modality == bittensor_pb2.Modality.IMAGE:
            return PyTorchSerializer.serialize_image( tensor )
        
        elif modality == bittensor_pb2.Modality.TEXT:
            return PyTorchSerializer.serialize_text( tensor )
        
        elif modality == bittensor_pb2.Modality.TENSOR:
            return PyTorchSerializer.serialize_tensor( tensor )
        
        else:
            raise NotImplementedError
            

    @staticmethod
    def serialize_text(tensor: torch.Tensor) -> bittensor_pb2.Tensor:
        """Serializes a torch.Tensor to an bittensor Tensor proto.

        Args:
            tensor (torch.Tensor): A list of strings.

        Returns:
            bittensor_pb2.Tensor: Serialized tensor as bittensor_pb2.proto. 
        """
        data_buffer = tensor.cpu().numpy().tobytes()
        dtype = torch_dtype_to_bittensor_dtype (tensor.dtype)
        shape = list(tensor.shape)
        proto = bittensor_pb2.Tensor(
                    version = bittensor.__version__,
                    buffer = data_buffer,
                    shape = shape,
                    dtype = dtype,
                    modality = bittensor_pb2.Modality.TEXT,
                    requires_grad = False)
        return proto
        
    @staticmethod
    def serialize_image(tensor: torch.Tensor) -> bittensor_pb2.Tensor:
        """Serializes a torch.Tensor image into a bittensor Tensor proto.

        Args:
            tensor (torch.Tensor): torch.Tensor of images to serialize.

        Returns:
            bittensor_pb2.Tensor: Serialized tensor as bittensor_pb2.proto. 
        """    
        data_buffer = tensor.cpu().numpy().tobytes()
        dtype = torch_dtype_to_bittensor_dtype (tensor.dtype)
        shape = list(tensor.shape)
        proto = bittensor_pb2.Tensor(
                    version = bittensor.__version__,
                    buffer = data_buffer,
                    shape = shape,
                    dtype = dtype,
                    modality = bittensor_pb2.Modality.IMAGE,
                    requires_grad = tensor.requires_grad)      
        return proto
    
    @staticmethod
    def serialize_tensor(tensor: torch.Tensor) -> bittensor_pb2.Tensor:
        """Serializes a torch.Tensor to an bittensor Tensor proto.

        Args:
            tensor (torch.Tensor): torch.Tensor to serialize.

        Returns:
            bittensor_pb2.Tensor: Serialized tensor as bittensor_pb2.proto. 
        """
        data_buffer = tensor.cpu().numpy().tobytes()
        dtype = torch_dtype_to_bittensor_dtype (tensor.dtype)
        shape = list(tensor.shape)
        proto = bittensor_pb2.Tensor(
                    version = bittensor.__version__,
                    buffer = data_buffer,
                    shape = shape,
                    dtype = dtype,
                    modality = bittensor_pb2.Modality.TENSOR,
                    requires_grad = tensor.requires_grad)      
        return proto
    
    
    @staticmethod
    def deserialize_image(proto: bittensor_pb2.Tensor) -> torch.Tensor:
        """Deserializes an bittensor_pb2.Tensor to a torch.Tensor object.

        Args:
            proto (bittensor_pb2.Tensor): Proto to derserialize.

        Returns:
            torch.Tensor: deserialized image tensor.
        """
        dtype = np.float32
        array = np.frombuffer(proto.buffer, dtype=np.dtype(dtype)).copy()
        shape = tuple(proto.shape)
        tensor = torch.as_tensor(array).view(shape).requires_grad_(proto.requires_grad)
        return tensor
        
    @staticmethod
    def deserialize_text(proto: bittensor_pb2.Tensor) -> torch.Tensor:
        """Deserializes an bittensor_pb2.Tensor to a torch.Tensor object.

        Args:
            proto (bittensor_pb2.Tensor): Proto to derserialize.

        Returns:
            torch.Tensor: deserialized text tensor.
        """
        dtype = bittensor_dtype_np_dtype(proto.dtype)
        array = np.frombuffer(proto.buffer, dtype=np.dtype(dtype)).copy()
        shape = tuple(proto.shape)
        tensor = torch.as_tensor(array).view(shape).requires_grad_(proto.requires_grad)
        return tensor
            
    @staticmethod
    def deserialize_tensor(proto: bittensor_pb2.Tensor) -> torch.Tensor:
        """Deserializes an bittensor_pb2.Tensor to a torch.Tensor object.

        Args:
            proto (bittensor_pb2.Tensor): Proto to derserialize.

        Returns:
            torch.Tensor: deserialized tensor.
        """
        dtype = bittensor_dtype_np_dtype(proto.dtype)
        array = np.frombuffer(proto.buffer, dtype=np.dtype(dtype)).copy()
        shape = tuple(proto.shape)
        tensor = torch.as_tensor(array).view(shape).requires_grad_(proto.requires_grad)
        return tensor