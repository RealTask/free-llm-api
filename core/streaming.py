"""
Streaming Support

Comprehensive async streaming support for LLM responses.
"""

import asyncio
import logging
from typing import Any, AsyncIterator, Callable, Dict, List, Optional, Union
from dataclasses import dataclass, field
import json

from .models import RequestContext, ResponseResult

logger = logging.getLogger(__name__)


@dataclass
class StreamChunk:
    """A chunk of streaming data."""
    content: str
    provider: str
    model: str
    chunk_id: int = 0
    finish_reason: Optional[str] = None
    usage: Optional[Dict[str, int]] = None
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "content": self.content,
            "provider": self.provider,
            "model": self.model,
            "chunk_id": self.chunk_id,
            "finish_reason": self.finish_reason,
            "usage": self.usage,
            "metadata": self.metadata,
        }


@dataclass
class StreamingResponse:
    """Complete streaming response."""
    request_context: RequestContext
    chunks: List[StreamChunk] = field(default_factory=list)
    provider: str = ""
    model: str = ""
    complete: bool = False
    error: Optional[str] = None
    usage: Optional[Dict[str, int]] = None
    
    @property
    def full_text(self) -> str:
        """Get the complete text from all chunks."""
        return "".join(chunk.content for chunk in self.chunks)
    
    def add_chunk(self, chunk: StreamChunk):
        """Add a chunk to the response."""
        self.chunks.append(chunk)
        if chunk.usage:
            self.usage = chunk.usage
        if chunk.finish_reason:
            self.complete = True
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "request_id": self.request_context.request_id,
            "provider": self.provider,
            "model": self.model,
            "complete": self.complete,
            "error": self.error,
            "usage": self.usage,
            "chunks_count": len(self.chunks),
            "full_text": self.full_text,
        }


class AsyncStreamingManager:
    """
    Manager for handling async streaming responses from providers.
    
    Provides unified streaming interface across different provider APIs.
    """
    
    def __init__(self):
        self._streaming_sessions: Dict[str, AsyncIterator] = {}
        self._callbacks: Dict[str, List[Callable[[StreamChunk], None]]] = {}
        self._lock = asyncio.Lock()
    
    async def stream(
        self,
        provider: Any,
        model: str,
        messages: Union[str, List[Dict[str, Any]]],
        request_context: Optional[RequestContext] = None,
        **kwargs
    ) -> AsyncIterator[StreamChunk]:
        """
        Stream responses from a provider.
        
        Args:
            provider: Provider instance
            model: Model name
            messages: Chat messages
            request_context: Optional request context
            **kwargs: Additional arguments
            
        Yields:
            StreamChunk: Streaming chunks
        """
        request_context = request_context or RequestContext(
            provider=provider.config.name if hasattr(provider, "config") else "unknown",
            model=model,
        )
        
        try:
            # Check if provider supports streaming
            if hasattr(provider, "stream_chat"):
                async for chunk in provider.stream_chat(model, messages, **kwargs):
                    yield StreamChunk(
                        content=chunk.get("content", ""),
                        provider=provider.config.name if hasattr(provider, "config") else "unknown",
                        model=model,
                        chunk_id=chunk.get("chunk_id", 0),
                        finish_reason=chunk.get("finish_reason"),
                        usage=chunk.get("usage"),
                    )
            elif hasattr(provider, "chat"):
                # Fallback: call chat and yield as single chunk
                response = await provider.chat(model, messages, **kwargs)
                yield StreamChunk(
                    content=response,
                    provider=provider.config.name if hasattr(provider, "config") else "unknown",
                    model=model,
                    chunk_id=0,
                    finish_reason="stop",
                )
            else:
                raise ValueError(f"Provider {provider} does not support chat or streaming")
                
        except Exception as e:
            logger.error(f"Streaming error: {e}")
            yield StreamChunk(
                content="",
                provider=provider.config.name if hasattr(provider, "config") else "unknown",
                model=model,
                chunk_id=0,
                finish_reason="error",
                metadata={"error": str(e)},
            )
    
    async def stream_with_callbacks(
        self,
        provider: Any,
        model: str,
        messages: Union[str, List[Dict[str, Any]]],
        on_chunk: Optional[Callable[[StreamChunk], None]] = None,
        on_complete: Optional[Callable[[StreamingResponse], None]] = None,
        on_error: Optional[Callable[[Exception], None]] = None,
        request_context: Optional[RequestContext] = None,
        **kwargs
    ) -> StreamingResponse:
        """
        Stream with callbacks for each event.
        
        Args:
            provider: Provider instance
            model: Model name
            messages: Chat messages
            on_chunk: Callback for each chunk
            on_complete: Callback when streaming completes
            on_error: Callback on error
            request_context: Optional request context
            **kwargs: Additional arguments
            
        Returns:
            StreamingResponse: Complete streaming response
        """
        request_context = request_context or RequestContext(
            provider=provider.config.name if hasattr(provider, "config") else "unknown",
            model=model,
        )
        
        response = StreamingResponse(
            request_context=request_context,
            provider=provider.config.name if hasattr(provider, "config") else "unknown",
            model=model,
        )
        
        try:
            async for chunk in self.stream(provider, model, messages, request_context, **kwargs):
                response.add_chunk(chunk)
                if on_chunk:
                    try:
                        on_chunk(chunk)
                    except Exception as e:
                        logger.error(f"Error in on_chunk callback: {e}")
                
                if chunk.finish_reason == "error":
                    raise Exception(chunk.metadata.get("error", "Unknown error"))
            
            response.complete = True
            if on_complete:
                try:
                    on_complete(response)
                except Exception as e:
                    logger.error(f"Error in on_complete callback: {e}")
                    
        except Exception as e:
            response.error = str(e)
            if on_error:
                try:
                    on_error(e)
                except Exception as callback_error:
                    logger.error(f"Error in on_error callback: {callback_error}")
        
        return response
    
    async def collect_stream(
        self,
        provider: Any,
        model: str,
        messages: Union[str, List[Dict[str, Any]]],
        request_context: Optional[RequestContext] = None,
        **kwargs
    ) -> StreamingResponse:
        """
        Collect all chunks from a streaming response.
        
        Args:
            provider: Provider instance
            model: Model name
            messages: Chat messages
            request_context: Optional request context
            **kwargs: Additional arguments
            
        Returns:
            StreamingResponse: Complete streaming response
        """
        response = StreamingResponse(
            request_context=request_context or RequestContext(
                provider=provider.config.name if hasattr(provider, "config") else "unknown",
                model=model,
            ),
            provider=provider.config.name if hasattr(provider, "config") else "unknown",
            model=model,
        )
        
        async for chunk in self.stream(provider, model, messages, request_context, **kwargs):
            response.add_chunk(chunk)
            if chunk.finish_reason == "error":
                response.error = chunk.metadata.get("error", "Unknown error")
                break
        
        response.complete = True
        return response
    
    def register_session(
        self,
        session_id: str,
        stream: AsyncIterator[StreamChunk]
    ):
        """
        Register a streaming session.
        
        Args:
            session_id: Session ID
            stream: Streaming iterator
        """
        self._streaming_sessions[session_id] = stream
        self._callbacks[session_id] = []
        logger.debug(f"Registered streaming session: {session_id}")
    
    def unregister_session(self, session_id: str):
        """
        Unregister a streaming session.
        
        Args:
            session_id: Session ID
        """
        if session_id in self._streaming_sessions:
            del self._streaming_sessions[session_id]
        if session_id in self._callbacks:
            del self._callbacks[session_id]
        logger.debug(f"Unregistered streaming session: {session_id}")
    
    def add_callback(
        self,
        session_id: str,
        callback: Callable[[StreamChunk], None]
    ):
        """
        Add a callback for a streaming session.
        
        Args:
            session_id: Session ID
            callback: Callback function
        """
        if session_id not in self._callbacks:
            self._callbacks[session_id] = []
        self._callbacks[session_id].append(callback)
    
    def remove_callback(
        self,
        session_id: str,
        callback: Callable[[StreamChunk], None]
    ):
        """
        Remove a callback from a streaming session.
        
        Args:
            session_id: Session ID
            callback: Callback function to remove
        """
        if session_id in self._callbacks:
            if callback in self._callbacks[session_id]:
                self._callbacks[session_id].remove(callback)
    
    async def broadcast_chunk(
        self,
        session_id: str,
        chunk: StreamChunk
    ):
        """
        Broadcast a chunk to all callbacks for a session.
        
        Args:
            session_id: Session ID
            chunk: Chunk to broadcast
        """
        if session_id in self._callbacks:
            for callback in self._callbacks[session_id]:
                try:
                    callback(chunk)
                except Exception as e:
                    logger.error(f"Error in callback for session {session_id}: {e}")


class StreamProcessor:
    """
    Processor for transforming and handling streaming data.
    """
    
    @staticmethod
    def process_text_chunk(text: str) -> str:
        """
        Process a text chunk (clean, normalize, etc.).
        
        Args:
            text: Raw text chunk
            
        Returns:
            str: Processed text
        """
        # Remove common streaming artifacts
        text = text.replace("▌", "")
        text = text.replace("\n\n", "\n")
        text = text.strip()
        return text
    
    @staticmethod
    def extract_json(text: str) -> Optional[Dict[str, Any]]:
        """
        Extract JSON from text if possible.
        
        Args:
            text: Text containing JSON
            
        Returns:
            Dict[str, Any]: Extracted JSON or None
        """
        try:
            # Try to parse as JSON
            return json.loads(text)
        except json.JSONDecodeError:
            # Try to extract JSON from text
            import re
            match = re.search(r'\{[^{}]*\}', text)
            if match:
                try:
                    return json.loads(match.group())
                except json.JSONDecodeError:
                    pass
        return None
    
    @staticmethod
    def format_streaming_response(
        chunk: StreamChunk,
        format_type: str = "text"
    ) -> Any:
        """
        Format a streaming chunk for output.
        
        Args:
            chunk: Stream chunk
            format_type: Output format (text, json, dict)
            
        Returns:
            Any: Formatted chunk
        """
        if format_type == "json":
            return json.dumps(chunk.to_dict())
        elif format_type == "dict":
            return chunk.to_dict()
        else:
            return chunk.content


class StreamAggregator:
    """
    Aggregator for combining multiple streams.
    """
    
    def __init__(self):
        self._streams: Dict[str, AsyncIterator] = {}
        self._results: Dict[str, List[StreamChunk]] = {}
    
    async def aggregate_streams(
        self,
        streams: Dict[str, AsyncIterator[StreamChunk]],
        strategy: str = "round_robin"
    ) -> AsyncIterator[Dict[str, StreamChunk]]:
        """
        Aggregate multiple streams into one.
        
        Args:
            streams: Dictionary of stream names to iterators
            strategy: Aggregation strategy (round_robin, merge, priority)
            
        Yields:
            Dict[str, StreamChunk]: Dictionary of stream name to latest chunk
        """
        if strategy == "round_robin":
            async for result in self._round_robin(streams):
                yield result
        elif strategy == "merge":
            async for result in self._merge(streams):
                yield result
        elif strategy == "priority":
            async for result in self._priority(streams):
                yield result
    
    async def _round_robin(
        self,
        streams: Dict[str, AsyncIterator[StreamChunk]]
    ) -> AsyncIterator[Dict[str, StreamChunk]]:
        """Round-robin aggregation."""
        stream_list = list(streams.items())
        index = 0
        
        while True:
            stream_name, stream = stream_list[index]
            try:
                chunk = await anext(stream)
                yield {stream_name: chunk}
                index = (index + 1) % len(stream_list)
            except StopAsyncIteration:
                # Remove completed stream
                stream_list.pop(index)
                if not stream_list:
                    break
                if index >= len(stream_list):
                    index = 0
    
    async def _merge(
        self,
        streams: Dict[str, AsyncIterator[StreamChunk]]
    ) -> AsyncIterator[Dict[str, StreamChunk]]:
        """Merge all streams, yielding as chunks arrive."""
        tasks = {}
        
        for name, stream in streams.items():
            tasks[name] = asyncio.create_task(self._consume_stream(name, stream))
        
        try:
            while tasks:
                done, _ = await asyncio.wait(
                    tasks.values(),
                    return_when=asyncio.FIRST_COMPLETED
                )
                
                for task in done:
                    name = [n for n, t in tasks.items() if t == task][0]
                    try:
                        chunk = task.result()
                        if chunk is not None:
                            yield {name: chunk}
                    except Exception:
                        pass
                    
                    # Remove completed task
                    del tasks[name]
                    
        except asyncio.CancelledError:
            # Cancel all tasks
            for task in tasks.values():
                task.cancel()
    
    async def _consume_stream(
        self,
        name: str,
        stream: AsyncIterator[StreamChunk]
    ) -> Optional[StreamChunk]:
        """Consume a single stream."""
        try:
            return await anext(stream)
        except StopAsyncIteration:
            return None
    
    async def _priority(
        self,
        streams: Dict[str, AsyncIterator[StreamChunk]]
    ) -> AsyncIterator[Dict[str, StreamChunk]]:
        """Priority-based aggregation (not implemented)."""
        # For now, use round-robin
        async for result in self._round_robin(streams):
            yield result


# Global streaming manager instance
_streaming_manager: Optional[AsyncStreamingManager] = None


def get_streaming_manager() -> AsyncStreamingManager:
    """Get the global streaming manager instance."""
    global _streaming_manager
    if _streaming_manager is None:
        _streaming_manager = AsyncStreamingManager()
    return _streaming_manager
