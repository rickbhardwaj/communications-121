function recorder = receivebits( b, G)
%UNTITLED Summary of this function goes here
%   Detailed explanation goes here
    global num_of_tones;
    global Fs;
    global duration;
    global onfreqs;
    global offfreqs;
    global synced;
    global signal_start;
    global bits;
    global Gen_mat;
    global chirp_sig;
    global special_chirp;
    global thebits;
    global sync_tone_intensities;
    global start_time;
    global countdown;
    countdown = 10;
    sync_tone_intensities = [];
    thebits = b;
    %global my_sig;
    %my_sig = signal;
    Gen_mat = G;
    bits = [];
    num_of_tones = 32;
    startfreq = 2000;
    endfreq = 10000;
    Fs= 150000;
    duration = .1;
    onfreqs = startfreq:(endfreq-startfreq)/(2.*num_of_tones):endfreq;
    offfreqs = onfreqs(1:2:length(onfreqs));
    onfreqs = onfreqs(2:2:length(onfreqs));
    %disp(offfreqs);
    %disp(onfreqs);
    synced = 0;
    signal_start = 1;
    t = 0:1/Fs:duration;
    chirp_sig = chirp(t,startfreq,duration,endfreq,'linear');
    t = 0:1/Fs:2*duration;
    special_chirp = chirp(t,startfreq,2*duration,endfreq,'linear');
    recorder = audiorecorder(Fs,24,1);
    recorder.TimerPeriod = duration;
    recorder.TimerFcn = {@getthebits};
    recorder.StopFcn = {@finish};
    record(recorder);

end

function getthebits(hobject,~)
    global num_of_tones;
    global Fs;
    global duration;
    global onfreqs;
    global offfreqs;
    global synced;
    global signal_start;
    global bits;
    look_ahead = .01;
    %global my_sig;
    signal = getaudiodata(hobject);
    %signal = my_sig;
    if(not(synced))
        if((signal_start < length(signal)) && length(signal(signal_start:end))>(duration*Fs*(2+look_ahead)))
            [synced,signal_start] = get_synced(signal,signal_start,Fs,duration);
        end
    else
        while ( (signal_start < length(signal)) && length(signal(signal_start:end))>(duration*Fs*(4+look_ahead)) )
            newbits = parse(signal(signal_start:(signal_start+floor(duration*Fs)-1)),Fs,num_of_tones,onfreqs,offfreqs,duration);
            signal_start = resync(signal,signal_start, Fs, duration);
            if(signal_start == -1)
                bits = bits(1:(end-num_of_tones));
                stop(hobject);
                break;
            else
                bits = [bits,newbits];
            end
        end
    end
end

function [synced, signal_start] = get_synced(signal,signal_start,Fs,duration)
    global sync_tone_intensities;
    global special_chirp;
    global start_time;
    look_ahead = .01;
    if(isempty(sync_tone_intensities))
        sync_tone_intensities = [Fs,Fs,Fs,Fs];
    end
    if (signal_start + floor(duration*Fs) > length(signal))
        disp('DID NOT DETECT START OF SIGNAL!!');
        synced = 1;
        return;
    end
    [curr_intensity,max_i] = max( abs(xcorr(signal(max([1,signal_start - floor(2*duration*Fs)]):(signal_start + floor(2*duration*Fs))) , special_chirp)));
    max_i = max_i - (2*floor(2*duration*Fs)+1 - length(special_chirp)); % xcorr funny thingies
    sync_tone_intensities(end) = curr_intensity;
    %disp(sync_tone_intensities);
    synced = 1;
    for i = 1:(length(sync_tone_intensities)-1)
        if(sync_tone_intensities(i)==0 || 5*sync_tone_intensities(i) >= curr_intensity)
            synced = 0;
        end
        sync_tone_intensities(i) = sync_tone_intensities(i+1);
    end
    if(synced == 1)
        disp('signal start at: ');
        disp(signal_start + max_i-floor(2*duration*Fs));
        signal_start = max_i-floor(2*duration*Fs)+signal_start-1;
        start_time = tic;
        sync_tone_intensities = [Fs,Fs,Fs,Fs];
    else
        signal_start = signal_start + floor(duration*Fs);
    end
end

function bits = parse(signal, Fs, num_of_tones, onfreqs, offfreqs, duration)
    global data;
    winsize = 3;
    H = abs(fft(signal));
    %data = [data;H(offfreqs(1)*duration:offfreqs(end)*duration)];
    %figure;
    %plot((offfreqs(1)):1/duration:(offfreqs(end)),H(offfreqs(1)*duration:offfreqs(end)*duration));
    bits = zeros(1,num_of_tones);
    for i = 1:num_of_tones
        fon = floor(onfreqs(i)*duration)+2;
        foff = floor(offfreqs(i)*duration)+2;
        %disp('stuff')
        %disp((fon-floor(winsize/2)):(fon+floor(winsize/2)));
        %disp([fon,foff])
        %disp((foff-floor(winsize/2)):(foff+floor(winsize/2)));
        %disp('end stuff');
        on_intensity = 2*sum(H((fon-floor(winsize/2)):(fon+floor(winsize/2))));
        off_intensity = 2*sum(H((foff-floor(winsize/2)):(foff+floor(winsize/2))));
        %disp([on_intensity, off_intensity])
        if(on_intensity>1*off_intensity)
            bits(i)=1;
        elseif(off_intensity > 1*on_intensity)
            bits(i)=0;
        else
            bits(i)=-1;
        end       
    end
end

function signal_start = resync(signal, signal_start,Fs, duration)
    global chirp_sig;
    %global special_chirp;
    %global sync_tone_intensities;
    %global countdown;
    look_ahead = .01;
    [max_intensity,max_i] = max( abs( xcorr( signal(max([1,signal_start-floor(Fs*duration*look_ahead)]):(signal_start+floor(Fs*duration*(1+look_ahead)))) , chirp_sig ) ) );
    max_i = max_i - (floor(Fs*duration*look_ahead)+floor(Fs*duration*(1+look_ahead))+1 - length(chirp_sig)); % xcorr nonsense
    %disp([max_i-floor(Fs*duration*look_ahead)-1,Fs*duration]);
    %asdf = signal(max([1,signal_start-floor(Fs*duration/10)]):(signal_start+floor(Fs*duration*(11/10))));
    %aaa = 0:1/Fs:floor(length(asdf)/Fs);
    %figure;
    %plot(aaa,asdf);
    %figure;
    %abc = xcorr(asdf,chirp_sig);
    %disp(length(abc));
    %disp(abc(floor(end/2)-10:floor(end/2)+10));
    %plot(abc);
    %if(countdown==2)
    %    countdown = countdown -1;
    %elseif(countdown==1)
    %    countdown = 0;
    %end
    %if(countdown==0)
    %    stopped = 1;
    %else
    %    curr_intensity = max( abs( xcorr( signal(max([1,signal_start-floor(Fs*duration*look_ahead)]):(signal_start+floor(Fs*duration*(3+look_ahead)))) , special_chirp ) ));
    %    sync_tone_intensities(end) = curr_intensity;
    %    prev_intensity = sync_tone_intensities(end-1);
    %    %disp(sync_tone_intensities);
    %    %disp(sync_tone_intensities);
    %    stopped = 1;
    %    for i = 1:(length(sync_tone_intensities)-2)
    %        if(sync_tone_intensities(i)==0 || 20*sync_tone_intensities(i) >= curr_intensity)
    %            stopped = 0;
    %        end
    %        %if(sync_tone_intensities(i)==0 || (i~=(length(sync_tone_intensities)-1) && 4*sync_tone_intensities(i) >= prev_intensity))
    %        %    stopped = 0;
    %        %end
    %        sync_tone_intensities(i) = sync_tone_intensities(i+1);
    %    end
    %    if(stopped)
    %        countdown = 2;
    %        disp('HELL YEAH');
    %        stopped = 0;
    %    end
    %end
    %if( stopped )
    %    %plot(signal(max([1,signal_start-floor(Fs*duration*look_ahead)]):(signal_start+floor(Fs*duration*(look_ahead+2)))))
    %    disp('received end at: ');
    %    disp(signal_start);
    %    signal_start = -1;
    %else
        signal_start = signal_start + max_i - floor(Fs*duration*look_ahead) - 1;
        if(max_i<(Fs*duration/2) || max_i>(Fs*duration*3/2))
            %disp('SYNC ERROR');
            disp('stop detected!');
            %figure;
            %plot(signal(max([1,signal_start-floor(Fs*duration/10)]):(signal_start+floor(Fs*duration*(11/10)))))
            %figure;
            %plot(xcorr(signal(max([1,signal_start-floor(Fs*duration/10)]):(signal_start+floor(Fs*duration*(11/10)))),chirp_sig));
            signal_start = -1;
        end
    %end
end

function finish(hobject,~)
    global Gen_mat;
    global bits;
    global thebits;
    global num_of_tones;
    global start_time;
    errored = 0;
    
    if(length(bits) <= 17 + 5 + num_of_tones*2)
        disp('Message was completely cutoff!!');
        errored = 1;
        return;
    end
    bits = bits((2*num_of_tones+1):end);
    %if(~checkhash(bits(1:5),bits(6:end)))
    %    disp('Hash did not match!')
    %    errored = 1;
    %end
    bits = bits(5+1:end);
    message_length = bi2de(bits(1:17));
    if(length(bits(1+17:end)) < message_length)
        disp('Did not get enough bits!');
        disp('Got this many bits: ');
        disp(length(bits((1+17):end)));
        disp('expected this many bits: ');
        disp(message_length);
        errored = 1;
    end
    if errored
        return;
    end
    %if(length(bits(1+17:end))-num_of_tones>message_length )
    %    disp('got too many bits, but we''ll see what happens :3');
    %end
    bits = bits((1+17):end);
    bits = bits(1:message_length);
    decoded_bits = decodebits(bits,Gen_mat);
    bits = bits((num_of_tones+1):end);
    %disp(bits);
    if(~(length(thebits) == length(bits)))
        disp('not the same length received!!');
        return;
    end
    disp('# of errors: ');
    num_err = sum(~(thebits == bits));
    disp(num_err);
    total_time = toc(start_time);
    disp('data rate: ');
    disp(length(decoded_bits)/total_time);
    %disp('error pos: ');
    %disp(~(thebits == bits));
    %disp('bits received:');
    %disp(decoded_bits);
    disp('error rate: ');
    disp(num_err/length(thebits));
    %sound(chirp(0:1/150000:1,0,1,10000),150000);
    %data = (getaudiodata(hobject));
    %data = data - mean(data);
    %data = data/max(abs(data));
    %sound(data,150000);
end

function decoded_bits = decodebits(bits,G)
    decoded_bits = bits;
end

function good = checkhash(hash,bits)
    prime = 31;
    hashbits = 0;
    i = 1;
    while (i<length(bits))
        hashbits = mod(hashbits + bi2de(bits(i:min([end,i+100]))),prime);
        i = i + 101;
    end
    good = (bi2de(hash)== hashbits);
end