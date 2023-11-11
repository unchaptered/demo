from injector import singleton, inject

# Module Dependencies
from modules.gpt.gpt_token_calculator import GptTokenCalculator
from modules.gpt.gpt_moderation_adaptor import GptModerationAdaptor

@singleton
class GptModule:
    
    @inject
    def __init__(self,
                 gptTokenCalculator: GptTokenCalculator,
                gptModerationAdaptor: GptModerationAdaptor) -> None:

        self.gptTokenCalculator = gptTokenCalculator
        self.gptModerationAdaptor = gptModerationAdaptor