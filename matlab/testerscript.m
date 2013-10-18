b = randi([0,1],[1,200]);
recorder = receivebits(b, 1);
pause(3);
player = sendbits(b,1);


%%

b = repmat([0,1,0,1,1,1,0,0,0,1],[1,20]);
recorder = receivebits(b, 1);
pause(3);
player = sendbits(b,1);


%%
% receiver test
b = repmat([0,1,0,1,1,1,0,0,0,1],[1,20]);
recorder = receivebits(b, 1);

%%

% sender test

b = repmat([0,1,0,1,1,1,0,0,0,1],[1,20]);
player = sendbits(b,1);
%%
b = randi([0,1],[1,8*1024]);
%b = [[1,1,0,0,0,0,1,0,0,0,0,0,1,1,0,0],[1,0,1,1,0,0,1,1,1,1,1,0,1,0,0,1]];
%b = repmat(b,1,2);
[signal , player] = sendbits(b,1);
extra_sin = sin(2*pi*2*(0:1/150000:3));
signal = [extra_sin, signal, extra_sin];
disp(max(abs(signal)));
disp(length(extra_sin));
sigma = .5;
signal = signal + sigma*rand([1,length(signal)]);
recorder = receivebits(b, 1, signal);
pause(3);

%%

% testing file on 1 computer

fid = fopen('test.jpg', 'r');
bytelist = fread(fid, '*uint8');
fclose(fid);
bitexpanded = dec2bin(bytelist(:), 8) - '0';
b = reshape( bitexpanded.', [], 1);
b = b';
recorder = receivebits(b, 1);
pause(3);
player = sendbits(b,1);

%%
% receive file
fid = fopen('test.jpg', 'r');
bytelist = fread(fid, '*uint8');
fclose(fid);
bitexpanded = dec2bin(bytelist(:), 8) - '0';
b = reshape( bitexpanded.', [], 1);
b = b';
recorder = receivebits(b, 1);

%%
% send file
fid = fopen('test.jpg', 'r');
bytelist = fread(fid, '*uint8');
fclose(fid);
bitexpanded = dec2bin(bytelist(:), 8) - '0';
b = reshape( bitexpanded.', [], 1);
b = b';
player = sendbits(b,1);