function player = sendbits( bits , G)
%sendbits sends bits
%   Detailed explanation goes here
    disp('sending the bits');
    %disp(bi2de(bits));
    
    num_of_tones = 32;
    bits = [zeros([1,num_of_tones]),bits];
    encoded_bits = encode_bits(bits,G);
    startfreq = 2000;
    endfreq = 10000;
    Fs = 150000;
    duration = .1;
    lengthbits = de2bi(length(encoded_bits),17);
    encoded_bits = [lengthbits,encoded_bits];
    encoded_bits = [encoded_bits,zeros([1,num_of_tones-mod(length(encoded_bits)+5,num_of_tones)])];
    hashbits = hash(encoded_bits);
    encoded_bits = [hashbits,encoded_bits];
    encoded_bits = [zeros([1,2*num_of_tones]),encoded_bits];
    onfreqs = startfreq:(endfreq-startfreq)/(2.*num_of_tones):endfreq;
    offfreqs = onfreqs(1:2:length(onfreqs));
    onfreqs = onfreqs(2:2:length(onfreqs));
    %for i = 1:num_of_tones;
    %fon = floor(onfreqs(i)*duration)+2;
    %foff = floor(offfreqs(i)*duration)+2;
    %disp('stuff')
    %disp((fon-floor(winsize/2)):(fon+floor(winsize/2)));
    %disp([fon,foff])
    %disp((foff-floor(winsize/2)):(foff+floor(winsize/2)));
    %disp('end stuff');
    %disp(onfreqs)
    %disp(offfreqs)
    %end
    t = 0:1/Fs:duration;
    chirp_sig = chirp(t,startfreq,duration,endfreq,'linear');
    t = 0:1/Fs:2*duration;
    special_chirp = chirp(t,startfreq,2*duration,endfreq,'linear');
    signal = special_chirp;
    for i = 1:num_of_tones:length(encoded_bits)
        next_sig = get_many_signal(encoded_bits(i:(i+num_of_tones-1)),duration,Fs,onfreqs,offfreqs)+chirp_sig;
        signal = [signal,next_sig./max(abs(next_sig))];
    end
    signal = [signal,special_chirp];
    player = audioplayer(signal, Fs);
    play(player);

end

function signal = get_many_signal(bits, duration, Fs, onfreqs, offfreqs)
    t = 0:1/Fs:duration;
    signal = t.*0;
    for i = 1:length(bits)
        if(bits(i)==0)
            %disp(offfreqs(i));
            signal = signal + sin(2*pi*offfreqs(i).*t);
        else
            %disp(onfreqs(i));
            signal = signal + sin(2*pi*onfreqs(i).*t);
        end
    end
end

function encoded_bits = encode_bits(bits,G)
    encoded_bits = bits;
end

function hashbits = hash(bits)
    prime = 31;
    hashbits = 0;
    i = 1;
    while (i<length(bits))
        hashbits = mod(hashbits + bi2de(bits(i:min([end,i+100]))),prime);
        i = i + 101;
    end
    hashbits = de2bi(hashbits,5);
end