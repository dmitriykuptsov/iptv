data<-read.table("results.dat");
agg<-aggregate(data, list(data$V2), mean);
print(agg);
pdf("aes_encryption_duration.pdf", height=4);
plot(agg$V2, agg$V1/1000, col="deepskyblue3", pch=3, lwd=5, main="", xlim=c(0, 64), ylim=c(0, 15), las=1, xlab="Size, MB", ylab="Average encryption time, s");
#points(agg$V2, agg$V1/1000, col="grey", lwd=4, type="l");
grid(col="grey", lwd=3);
dev.off();
