import os
import sys

sys.path.append('{}/lib'.format('/'.join((os.path.realpath(__file__)).split('/')[:-3])))

__all__ = []


minimum_required_fields = ('type', 'value')

checking_error = 'containing at least a "type" field and a "value" field'
standard_error_message = 'This module requires an "attribute" field as input'


def check_input_attribute(attribute, requirements=minimum_required_fields):
    return all(feature in attribute for feature in requirements)
