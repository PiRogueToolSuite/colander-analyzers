import json
import logging
import uuid

import dns.resolver

from colander_analyzers.modules.enrichment import check_input_attribute
from colander_analyzers.modules.model import Observable, Relation, ColanderJsonEncoder, ColanderRegistry
from colander_analyzers.modules.utils import is_ipv4, is_ipv6

module_errors = {'error': 'Error'}
module_attributes = {'input': ['value', 'reference'], 'type': ['domain']}
module_info = {'version': '1',
               'author': 'Esther Onfroy',
               'description': 'Map DNS information for a domain or an IP address. Based on Harpoon (https://github.com/Te-k/harpoon)',
               'module-type': ['enrich']}
module_config = []

log = logging.getLogger('colander-analyzers>dns_records')

all_types = [
    'NONE', 'A', 'NS', 'MD', 'MF', 'CNAME', 'SOA', 'MB', 'MG',
    'MR', 'NULL', 'WKS', 'PTR', 'HINFO', 'MINFO', 'MX', 'TXT', 'RP',
    'AFSDB', 'X25', 'ISDN', 'RT', 'NSAP', 'NSAP-PTR', 'SIG', 'KEY',
    'PX', 'GPOS', 'AAAA', 'LOC', 'NXT', 'SRV', 'NAPTR', 'KX', 'CERT',
    'A6', 'DNAME', 'OPT', 'APL', 'DS', 'SSHFP', 'IPSECKEY', 'RRSIG',
    'NSEC', 'DNSKEY', 'DHCID', 'NSEC3', 'NSEC3PARAM', 'TLSA', 'HIP',
    'CDS', 'CDNSKEY', 'CSYNC', 'SPF', 'UNSPEC', 'EUI48', 'EUI64',
    'TKEY', 'TSIG', 'IXFR', 'AXFR', 'MAILB', 'MAILA', 'ANY', 'URI',
    'CAA', 'TA', 'DLV']


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

    for a in all_types:
        try:
            answers = dns.resolver.resolve(input_data.get('value'), a)
            for rdata in answers:
                txt = rdata.to_text()
                observable_id = str(uuid.uuid4())
                ip_id = None
                registry.a(Observable(
                    id=observable_id,
                    type='dns_record',
                    value=f'{a} {txt}'
                ))
                registry.a(Relation(
                    id=str(uuid.uuid4()),
                    name='related to',
                    obj_from=f'{observable_id}',
                    obj_to=f'{target_id}',
                ))
                if is_ipv4(txt):
                    ip_id = str(uuid.uuid4())
                    registry.a(Observable(
                        id=ip_id,
                        type='ipv4',
                        value=f'{txt}',
                    ))
                elif is_ipv6(txt):
                    ip_id = str(uuid.uuid4())
                    registry.a(Observable(
                        id=ip_id,
                        type='ipv6',
                        value=f'{txt}',
                    ))
                if ip_id:
                    registry.a(Relation(
                        id=str(uuid.uuid4()),
                        name='resolves',
                        obj_from=f'{ip_id}',
                        obj_to=f'{target_id}',
                    ))
        except Exception as e:
            logging.debug(e)

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
            "reference": "990cbd78-f73f-4528-9f58-361ecbd110cd",
            "obj_type": "observable",
            "type": "domain",
            "value": "google.com"
        },
        "module": "resolve_dns"
    }
    response = handler(json.dumps(input_data))
    print(json.dumps(response, cls=ColanderJsonEncoder))
