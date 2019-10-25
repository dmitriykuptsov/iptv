data<-scan("cpu_usage_rpi.dat");
pdf("cpu_usage_rpi.pdf");
par(mfrow=c(2,1))
summary(data);
hist(data, col="dark blue", main="", xlab="CPU utilization, %", ylab="Frequency");
#grid(lwd=2, col="black");
plot(data, col="deepskyblue3", lwd=3, xlab="Sample", ylab="CPU utilization, %");
#grid(lwd=2, col="black");
dev.off();
