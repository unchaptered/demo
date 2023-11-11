from injector import singleton, inject

# Module Dependencies
from modules.aws.aws_rekognition_moderation_adaptor import AwsRekognitionModerationAdaptor

@singleton
class AwsRekognitionModule:
    
    @inject
    def __init__(self,
                 awsRekognitionModerationAdaptor: AwsRekognitionModerationAdaptor) -> None:
        self.awsRekognitionModerationAdaptor = awsRekognitionModerationAdaptor