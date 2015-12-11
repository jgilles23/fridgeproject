close all
load('allData.mat')
for i = 1:length(unixTime)
    if abs(fridgeTemp(i)) > 120
        fridgeTemp(i) = 50;
    end
    if abs(outsideTemp(i)) > 120
        outsideTemp(i) = 60;
    end
end
%unixTime = unixTime - 1.44*10^9;

%% 
figure
hold on
plot(unixTime,fridgeTemp);
plot(unixTime,outsideTemp);
plot(unixTime,doorPosition*40 + 38);

%%
openUnixTime = [];
for i = 2:length(doorPosition)
    if doorPosition(i) == 0 && doorPosition(i-1) == 1
        openUnixTime(end+1,1) = unixTime(i);
    end
end
openUnixTime

%%
csvwrite('open_data.csv',openUnixTime);

%% DISCRITIZE INTO 5 MIN SEGMENTS
prevTime = 0;
u = unixTime(2:150:end,1); %Unix time
f = fridgeTemp(2:150:end,1); %temp inside the fridge
a = outsideTemp(2:150:end,1); %temp outside the fridge
L = length(u);

figure
hold on
plot(u,f);
plot(u,a-30);

%% Hold half the data for later analysis
u1 = u(1:floor(end/2));
u2 = u(floor(end/2):end);
f1 = f(1:floor(end/2));
f2 = f(floor(end/2):end);
a1 = a(1:floor(end/2));
a2 = a(floor(end/2):end);

%% figure out when the compressor is on
c = zeros(length(f),1); %compressor state
for i = 1:length(f)-1
    if f(i) > f(i+1)
        c(i) = 1;
    end
end

%modify compressor to not count instants
for i = 1:length(f1)-2
    if c(i) && not(c(i+1)) && c(i+2)
        c(i+1) = not(c(i+1));
    end
end

c1 = c(1:floor(end/2));
c2 = c(floor(end/2):end);

timesub = 1.446*10^9;
figure
hold on
plot(u1-timesub,f1);
plot(u1-timesub,a1-30);
u1plot = u1(c1==1);
c1plot = c1(c1==1);
plot(u1plot-timesub, c1plot+43, 'o', 'MarkerSize', 1);

%% Save as CSV File
csvwrite('fridge_data.csv',[u1,f1,a1,c1]);

%% Check regression
xf = 0.98816669;
xa = 0.00940391;
xc = -0.33486184;

ef = zeros(length(u2),1);
ef(1) = f2(1);
for i = 2:length(u2)
    ef(i) = xf*ef(i-1) + xa*a2(i-1) + xc*c2(i-1);
end

timesub = 1.446*10^9;
figure
hold on
plot(u2-timesub,f2);
plot(u2-timesub,a2-30);
u2plot = u2(c2==1);
c2plot = c2(c2==1);
plot(u2plot-timesub, c2plot+43, 'o', 'MarkerSize', 1);
plot(u2-timesub,ef);
legend('Fridge Temp','Room Temp (minus 30 deg)','Compressor State','Predicted Fridge Temp')
ylabel('Temperature (deg F)')
xlabel('Time (seconds)')
title('Predicted Fridge Temperature Based on Linear Model')