data<-read.table("encoding_results.dat");
agg<-aggregate(data, list(data$V2), mean);
print(agg);
pdf("mpeg2_ts_conversion.pdf", height=4);
plot(agg$V2, agg$V1/1000, col="deepskyblue3", pch=3, lwd=5, las=1, xlim=c(0, 100), ylim=c(0, 15), main="", xlab="Capturing duration, seconds", ylab="Average conversion time, s");
grid(col="grey", lwd=3);
dev.off();
