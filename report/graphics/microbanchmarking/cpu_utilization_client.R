data<-scan("results_cpu_client.dat");
pdf("cpu_usage_client.pdf");
summary(data);
par(mfrow=c(2,1))
hist(data, col="dark blue", main="", xlab="CPU utilization, %", ylab="Frequency");
#grid(lwd=2, col="black");
plot(data, col="deepskyblue3", lwd=3, xlab="Sample", ylab="CPU utilization, %");
#grid(lwd=2, col="black");
dev.off();
