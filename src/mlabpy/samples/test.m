% Simple collection of some test code for MlabPy.
%
% Copyright (C) 2015, led02 <mlabpy@led-inc.eu>

A = [0 1 2 3]
A{end+1} = 4
disp(A)
assert(length(A) == 5, 'LENGTH')
assert(A{1} == 0, 'First')
assert(A{end-1} == 3, 'Last but one')
assert(A{end} == 4, 'Last')
