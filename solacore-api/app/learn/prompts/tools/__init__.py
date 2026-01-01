"""学习工具提示词"""

from .chunking import TOOL_PROMPT as CHUNKING_PROMPT
from .dual_coding import TOOL_PROMPT as DUAL_CODING_PROMPT
from .error_driven import TOOL_PROMPT as ERROR_DRIVEN_PROMPT
from .feynman import TOOL_PROMPT as FEYNMAN_PROMPT
from .grow import TOOL_PROMPT as GROW_PROMPT
from .interleaving import TOOL_PROMPT as INTERLEAVING_PROMPT
from .pareto import TOOL_PROMPT as PARETO_PROMPT
from .retrieval import TOOL_PROMPT as RETRIEVAL_PROMPT
from .socratic import TOOL_PROMPT as SOCRATIC_PROMPT
from .spaced import TOOL_PROMPT as SPACED_PROMPT

__all__ = [
    "CHUNKING_PROMPT",
    "DUAL_CODING_PROMPT",
    "ERROR_DRIVEN_PROMPT",
    "FEYNMAN_PROMPT",
    "GROW_PROMPT",
    "INTERLEAVING_PROMPT",
    "PARETO_PROMPT",
    "RETRIEVAL_PROMPT",
    "SOCRATIC_PROMPT",
    "SPACED_PROMPT",
]
