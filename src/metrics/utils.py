"""Utility functions for metrics handling."""

from configuration import configuration
from client import LlamaStackClientHolder, AsyncLlamaStackClientHolder
from log import get_logger
import metrics

logger = get_logger(__name__)


async def setup_model_metrics() -> None:
    """Perform setup of all metrics related to LLM model and provider."""
    model_list = []
    if configuration.llama_stack_configuration.use_as_library_client:
        model_list = await AsyncLlamaStackClientHolder().get_client().models.list()
    else:
        model_list = LlamaStackClientHolder().get_client().models.list()

    models = [
        model
        for model in model_list
        if model.model_type == "llm"  # pyright: ignore[reportAttributeAccessIssue]
    ]

    default_model_label = (
        configuration.inference.default_provider,  # type: ignore[reportAttributeAccessIssue]
        configuration.inference.default_model,  # type: ignore[reportAttributeAccessIssue]
    )

    for model in models:
        provider = model.provider_id
        model_name = model.identifier
        if provider and model_name:
            # If the model/provider combination is the default, set the metric value to 1
            # Otherwise, set it to 0
            default_model_value = 0
            label_key = (provider, model_name)
            if label_key == default_model_label:
                default_model_value = 1

            # Set the metric for the provider/model configuration
            metrics.provider_model_configuration.labels(*label_key).set(
                default_model_value
            )
            logger.debug(
                "Set provider/model configuration for %s/%s to %d",
                provider,
                model_name,
                default_model_value,
            )
