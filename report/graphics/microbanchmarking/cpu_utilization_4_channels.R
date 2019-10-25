data<-scan("cpu_usage_rpi_4_channels.dat");
summary(data);
pdf("cpu_usage_rpi_4_channels.pdf", height=4);
#par(mfrow=c(2,1))
hist(data, col="dark blue", main="", xlab="CPU utilization, %", ylab="Frequency");
#grid(lwd=2, col="black");
#plot(data, col="dark red", lwd=3, xlab="Sample", ylab="CPU utilization, %");
#grid(lwd=2, col="black");
dev.off();
