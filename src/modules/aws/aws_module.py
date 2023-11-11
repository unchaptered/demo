from injector import singleton, inject

# Module Dependencies
from modules.aws.aws_rekognition_module import AwsRekognitionModule

@singleton
class AwsModule:
    
    @inject
    def __init__(self,
                 awsRekognitionModule: AwsRekognitionModule) -> None:
        self.awsRekognitionModule = awsRekognitionModule