% Simple collection of some test code for MlabPy.
%
% Copyright (C) 2015, led02 <mlabpy@led-inc.eu>

function primes = primes(limit)
    primes = [ 2, 3 ];
    curr = 3;
    output_interval = 25
    
    while curr<limit
        curr += 2;
        curr_sqrt = sqrt(curr);
        for n=primes
            if n>curr_sqrt
                primes{end+1} = curr;
                % primes = [primes curr];
                break
            elseif mod(curr, n) == 0
                break
            end
        end
    end
