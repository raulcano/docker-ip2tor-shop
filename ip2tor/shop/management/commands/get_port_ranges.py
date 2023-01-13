from django.core.management.base import BaseCommand
from shop.models import Host
from itertools import chain
from rest_framework.authtoken.models import Token

class Command(BaseCommand):
    """
    List the string of port ranges for the environment file, in the right format to load a series of port ranges in a host
    It takes as an argument a list of individual ports and generates 2 strings. 
    The first string includes the port ranges corresponding to the passed input
    The second string includes the remaining ranges of the full spance (from min to max), removing the ports in the input
    - 
        Examples:
        
        python3 manage.py get_port_ranges --ports=1 --min_port_value=10000 --max_port_value=65555


    """
    
    absolute_min_value = 1
    absolute_max_value = 65535

    def add_arguments(self, parser):
        parser.add_argument("--min_port_value", required=False, default=self.absolute_min_value)
        parser.add_argument("--max_port_value", required=False, default=self.absolute_max_value)
        parser.add_argument("--ports", required=True)
    
    def onlyOneDigitDifferent(self, number):
        # convert the integer to a string, then to a set, and check if there is exactly 2 elements in the set

        number_str = str(number)
        number_list = list(number_str)
        number_set = set(number_str)
        if len(number_set) == 2:
            for x in number_set:
                if number_list.count(x) == 1 :
                    return True
        return False

            

    
    def getSilverPorts(self, min, max):
        res = ''
        

        for i in range(min, max):
            if self.onlyOneDigitDifferent(i):
                res = res + ',' + str(i)
        print(res)
        res = res.strip(',')
        return res

    def range_between(self, start, end, includeExtremes=None):
        if 'both' == includeExtremes and (end - start) >= 0:
            return str(start) + ',' + str(end)
        elif 'right' == includeExtremes and (end - start) >= 1:
            return str(start + 1) + ',' + str(end) 
        elif 'left' == includeExtremes and (end - start) >= 1:
            return str(start) + ',' + str(end - 1) 
        elif not includeExtremes and (end - start) >= 2:
            return str(start + 1) + ',' + str(end - 1)
        else:
            return False

    def handle(self, *args, **options):
        
        
        
        
        min_port = int(options["min_port_value"])
        max_port = int(options["max_port_value"])
        #Check that min and max are valid
        if min_port < self.absolute_min_value or min_port > self.absolute_max_value:
            self.stdout.write(f'ERROR: "min_port_value" ({min_port}) must be a value between {self.absolute_min_value} and {self.absolute_max_value}')
            return

        if max_port < self.absolute_min_value or max_port > self.absolute_max_value:
            self.stdout.write(f'ERROR: "max_port_value" ({max_port}) must be a value between {self.absolute_min_value} and {self.absolute_max_value}')
            return

        if min_port > max_port:
            self.stdout.write(f'ERROR: "min_port_value" ({min_port}) cannot be greater than "max_port_value" ({max_port})')
            return


        ports = options["ports"]
        if ports == 'premium':
            ports = '11111,22222,33333,44444,55555'
        elif ports == 'silver':
            ports = self.getSilverPorts(min_port, max_port)
        elif ports == 'premium_and_silver':
            ports = '11111,22222,33333,44444,55555,' + self.getSilverPorts(min_port, max_port)
        
        port_list_original = [int(i) for i in ports.split(',')]
        port_list_extended = port_list_original.copy()

        

        # add min and append max ports (we can add them both at the end, since we will sort the list later)
        port_list_extended.append(min_port)
        port_list_extended.append(max_port)

        # sort the port list from lower to higher
        port_list_extended.sort()

        # remove all values lower than min_port and higher than max_port
        port_list_extended = [x for x in port_list_extended if x >= min_port and x <= max_port]

        # remove duplicates from port_list_extended
        port_list_no_dups = []
        [port_list_no_dups.append(x) for x in port_list_extended if x not in port_list_no_dups]

        
        i = 0
        res1 = ""
        res2 = ""

        while i < len(port_list_no_dups) :
            ports_range = False

            res1 = res1 + ':' + str(port_list_no_dups[i]) + ',' + str(port_list_no_dups[i]) if port_list_no_dups[i] in port_list_original else res1

            if i < len(port_list_no_dups) - 1:
                if i == 0 and not port_list_no_dups[i] in port_list_original:
                    ports_range = self.range_between(port_list_no_dups[i], port_list_no_dups[i+1], includeExtremes='left')
                elif i == len(port_list_no_dups) - 2 and not port_list_no_dups[i+1] in port_list_original:
                    ports_range = self.range_between(port_list_no_dups[i], port_list_no_dups[i+1], includeExtremes='right')
                else:
                    ports_range = self.range_between(port_list_no_dups[i], port_list_no_dups[i+1])
            
            if (False != ports_range):
                res2 = res2 + ':' + ports_range

            i = i + 1
        
        
        res1 = res1.strip(':')
        res2 = res2.strip(':')


        self.stdout.write(f'This is the string for the ports passed in the input ({port_list_original})')
        self.stdout.write(f'{res1}')

        self.stdout.write(f'This is the string for the remaining port ranges opposite to the ones passed in the input')
        self.stdout.write(f'{res2}')

        return

        
            


        