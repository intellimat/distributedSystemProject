class NetworkException(Exception):
    def __init__(self, message):
        self.message = message

class ProcessorAddressNotFound(Exception):
    ''' The processor is not present in the file. '''
    def __init__(self, message):
        self.message = message
