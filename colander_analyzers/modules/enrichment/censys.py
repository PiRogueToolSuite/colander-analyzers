import json
import logging
import uuid

from censys.search import CensysHosts

from colander_analyzers import ColanderJsonEncoder
from colander_analyzers.modules.enrichment import check_input_attribute
from colander_analyzers.modules.model import Observable, Relation, ColanderRegistry

module_errors = {'error': 'Error'}
module_attributes = {'input': ['value', 'reference', 'type', 'censys_id', 'censys_key'], 'type': ['ipv4', 'ipv6']}
module_info = {'version': '1',
               'author': 'Esther Onfroy',
               'description': 'Get information about a given IP address from Censys.',
               'module-type': ['enrich']}
module_config = []

log = logging.getLogger('colander-analyzers>censys')


def handler(q=False):
    if q is False:
        return False
    request = json.loads(q)
    input_data = request.get('input')
    if not check_input_attribute(input_data, module_attributes.get('input')):
        return {
            'error': f'Some input information are missing, please check the module inputs requirements {module_attributes}'}

    registry = ColanderRegistry()
    target_id = input_data.get('reference')
    target = input_data.get('value')

    # h = CensysHosts(
    #     input_data.get('censys_id'),
    #     input_data.get('censys_key'),
    # )
    # host = h.view(target)

    response = json.load(open('/home/esther/Gre/projects/pts/colander-analyzers/censys.json'))
    location = response.get('location', None)
    autonomous_system = response.get('autonomous_system', None)
    services = response.get('services', None)
    dns = response.get('dns', None)
    if location:
        _id = str(uuid.uuid4())
        attributes = []
        country = location.get('country', '')
        country_code = location.get('country_code', '')
        coordinates = location.get('coordinates', None)
        if coordinates:
            attributes.append({
                'latitude': coordinates.get('latitude')
            })
            attributes.append({
                'longitude': coordinates.get('longitude')
            })
        registry.a(Observable(
            id=_id,
            type='location',
            value=f'{country_code} - {country}',
            attributes=attributes
        ))
        registry.a(Relation(
            name='located at',
            obj_from=target_id,
            obj_to=_id,
        ))
    if autonomous_system:
        _id = str(uuid.uuid4())
        attributes = [
            {'name': autonomous_system.get('name', '')},
            {'bgp_prefix': autonomous_system.get('bgp_prefix', '')},
            {'country_code': autonomous_system.get('country_code', '')},
        ]
        registry.a(Observable(
            id=_id,
            type='asn',
            value=autonomous_system.get('asn'),
            attributes=attributes,
            description=autonomous_system.get('description')
        ))
        registry.a(Relation(
            name='belongs to',
            obj_from=target_id,
            obj_to=_id
        ))
    if dns and 'names' in dns:
        dns_names = dns.get('names')
        for dns_name in dns_names:
            _id = str(uuid.uuid4())
            registry.a(Observable(
                id=_id,
                type='domain',
                value=dns_name
            ))
            registry.a(Relation(
                name='resolves',
                obj_from=target_id,
                obj_to=_id,
            ))

    response = {
        'input': input_data,
        'results': registry.all()
    }
    return response


def introspection():
    return module_attributes


def version():
    module_info['config'] = module_config
    return module_info


if __name__ == '__main__':
    input_data = {
        "input": {
            "reference": "980cbd78-f73f-4528-9f58-361ecbd110cd",
            "obj_type": "observable",
            "type": "ipv4",
            "value": "",
            "censys_id": "",
            "censys_key": "",

        },
        "module": "censys"
    }
    response = handler(json.dumps(input_data))
    print(json.dumps(response, cls=ColanderJsonEncoder))
