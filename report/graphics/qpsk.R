t<-c(seq(0, 0.975, 0.025), 
	 seq(1, 1.975, 0.025),
	 seq(2, 2.975, 0.025),
	 seq(3, 3.975, 0.025));
#print(length(t));
i<-c(rep(1, 40), 
	rep(-1, 40), 
	rep(1, 40), 
	rep(-1, 40));
#print(length(i));
q<-c(rep(1, 40), 
	rep(1, 40), 
	rep(-1, 40), 
	rep(-1, 40));
#print(length(q));
#q<-c(1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1,
#	 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1,
#     -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1,
#     -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1);
f<-5;
pdf("qpsk.pdf");
par(mfrow=c(3,1));
plot(t, i, col="dark blue", main="I(t)", ylab="I(t)", xlab="Time, s", type="l", lwd=3);
grid(col="black");
plot(t, q, col="skyblue", main="Q(t)", ylab="Q(t)", xlab="Time, s", type="l", lwd=3);
grid(col="black");
#plot(t, q, col="skyblue", main="", ylab="Q(t)", xlab="Time, s");
yt = i*cos(2*pi*f*t) - q*sin(2*pi*f*t);
plot(t, yt, main="Modulated signal", xlab="Time, s", ylab="y(t)", type="l", lwd=3, col="deepskyblue4");
grid(col="black")
dev.off();

pdf("qpsk_demod.pdf");
par(mfrow=c(2,1));
plot(t, yt * cos(2*pi*f*t), col="dark blue", lwd=3, main="I(t)", xlab="Time, s", ylab="Amplitude", type="l");
grid(col="black");
plot(t, -yt * sin(2*pi*f*t), col="deepskyblue4", lwd=3, main="Q(t)", xlab="Time, s", ylab="Amplitude", type="l"); 
grid(col="black");
#plot(t, -1 - sqrt(2) * sin(2*pi*f*t) * sin(2*pi*f*t + 3*pi/4), col="deepskyblue4", lwd=3, main="I(t)", xlab="Time, s", ylab="Amplitude", type="l"); 
#grid(col="black");
#plot(t, 1 - sqrt(2) * cos(2*pi*f*t) * sin(2*pi*f*t + 3*pi/4), col="deepskyblue4", lwd=3, main="Q(t)", xlab="Time, s", ylab="Amplitude", type="l"); 
#grid(col="black");
dev.off()

#alpha <- 0.1;
alpha <- (2*pi*1/40.0*f)/(2*pi*1/40.0*f+1);
print(paste("Alpha:", alpha));
pdf("qpsk_demod_lowpass.pdf");
par(mfrow=c(2,1));
# Demodulation 
zt <- yt * cos(2*pi*f*t);
# Exponentially weighted moving average:
# We need to smooth out high frequency component of the signal
r <- c();
c = 1;
for (s in zt) {
	if (c==1) {
		r[c] <- s; 
	} else {
		r[c] <- alpha * s + (1-alpha) * r[c-1]; 
	}
	c <- c + 1;
}
plot(t, r, col="dark blue", lwd=3, main="I(t)", xlab="Time, s", ylab="y(t)", type="l");
grid(col="black");
# Demodulation
zt <- -yt * sin(2*pi*f*t);
# Exponentially weighted moving average:
# We need to smooth out high frequency component of the signal
r <- c();
c = 1;
for (s in zt) {
	if (c==1) {
		r[c] <- s; 
	} else {
		r[c] <- alpha * s + (1-alpha) * r[c-1]; 
	}
	c <- c + 1;
}
plot(t, r, col="deepskyblue4", lwd=3, main="Q(t)", xlab="Time, s", ylab="y(t)", type="l");
grid(col="black");
dev.off();
