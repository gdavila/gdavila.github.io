---
title: "CER/CCER, Partial Service, and TCP Throughput in DOCSIS 3.0"
excerpt: "How codeword errors, channel bonding, and Partial Service shape TCP throughput on a DOCSIS 3.0 cable modem."
layout: post
permalink: /internet/PartialService/2018-02-01-PartialService/
categories: ["Data Communications"]
date: 2018-02-01 00:00:00 -0300
math: true
---

TCP throughput depends mainly on three variables: the round-trip time ($$RTT$$) of the path, the maximum segment size ($$MSS$$, which is in turn bounded by the MTU), and the packet loss rate ($$p$$) at the IP layer. In DOCSIS networks, the IP packet loss is largely driven by physical-layer errors, i.e., by the Codeword Error Ratio (CER) and the Correctable Codeword Error Ratio (CCER).

DOCSIS 3.0 adds two more variables to the picture: channel bonding, which spreads traffic over several downstream carriers, and *Partial Service* (PS), which allows the Cable Modem Termination System (CMTS) to stop using an impaired carrier. In this post, we briefly discuss how these variables interact and what they mean for the throughput a Cable Modem (CM) actually achieves. We first introduce a simple throughput model and compare it with laboratory measurements. Then, we look at the relation between CER and CCER. Finally, we show how Partial Service changes the picture when the Signal-to-Noise Ratio (SNR) of a carrier degrades.

# TCP throughput

A well-known approximation of the steady-state TCP throughput, proposed by Mathis et al., is:

$$
T_{tcp} \approx \frac{MSS}{RTT} \cdot \frac{C}{\sqrt{p}}
$$

where $$C$$ is a constant close to 1 that depends on the acknowledgement strategy. In the rest of this post, we use $$C = 1$$.

The packet loss $$p$$ depends on how codeword errors translate into IP packet losses. An IP packet is lost when any of the codewords that carry it is uncorrectable, so a single packet is exposed to several codewords. Additionally, with channel bonding, packets are distributed over the $$n_{ch}$$ bonded carriers. If only one carrier is impaired, only about $$1/n_{ch}$$ of the packets travel through it. Hence, we approximate:

$$
p \approx cer \cdot \frac{ip_{size}}{codeword_{size}} \cdot \frac{1}{n_{ch}} \approx \frac{7 \cdot cer}{n_{ch}}
$$

where $$cer$$ is the CER of the impaired carrier (as a fraction, not a percentage) and the factor of 7 is the approximate number of codewords that carry one IP packet: a 1500-byte packet over 204-byte Reed-Solomon codewords (i.e., 188-byte MPEG-TS packets plus 16 bytes of FEC parity) spans roughly 7 codewords. Said differently, the more carriers in the bonding group, the smaller the share of traffic exposed to the impaired carrier, and the higher the resulting throughput for the same CER.

To check this behaviour in practice, we measured TCP throughput in the laboratory for different CER values on a single impaired carrier, with two bonding configurations: 20 and 8 channels. The CM service was provisioned at a maximum of 50 Mbps (red line in the figure below). Each point is one measurement, and the blue curve is a smoothed trend with its confidence band.

![Measured TCP throughput versus CER for 20-channel and 8-channel bonding, with one impaired carrier](/internet/PartialService/unnamed-chunk-1-1.png)

With 20 bonded channels, the CM still reaches the provisioned 50 Mbps at a CER of 0.01%, whereas with 8 channels the throughput has already dropped to roughly 25 Mbps at the same CER. In both cases, the throughput falls below 10 Mbps once the CER exceeds approximately 0.3%.

The next figure shows the throughput predicted by the model for 24 and 8 bonded channels. We used $$MSS = 1460$$ bytes and RTT values drawn from the distribution we measured on the path (mean 27.5 ms, standard deviation 26.5 ms, minimum 9 ms), which explains the spread of the points.

![Theoretical TCP throughput versus CER for 24-channel and 8-channel bonding, with one impaired carrier](/internet/PartialService/unnamed-chunk-3-1.png)

The model reproduces the main trend of the measurements: throughput decreases with CER, and larger bonding groups are more tolerant to the same error ratio. However, the model is optimistic. For instance, for 8 channels at a CER of 0.01%, it predicts roughly 40–45 Mbps, while we measured roughly 25 Mbps. This gap is expected to some extent: the Mathis approximation ignores retransmission timeouts, and the loss model assumes that errors are independent and spread evenly over time, which is rarely the case with real interference. Therefore, we use the model to reason about trends and orders of magnitude rather than to predict exact values.

# CER and CCER

CER and CCER are the percentages of codewords that arrive with errors that the Forward Error Correction (FEC) cannot correct, and of codewords that arrive with errors that the FEC can correct, respectively.

In theory, only the CER affects the service, since uncorrectable codewords are lost, whereas correctable codewords are fully recovered. In practice, however, we never observed CER without CCER: the same impairment that produces uncorrectable codewords also produces a much larger number of correctable ones. The next figure shows this relation for a 20-channel bonding group. Each point is one measurement, and its colour encodes the TCP throughput.

![CER versus CCER for a 20-channel bonding group, coloured by TCP throughput](/internet/PartialService/unnamed-chunk-2-1.png)

CER and CCER grow together. While the CCER stays below roughly 10% (and the CER below about 0.03%), the throughput remains close to the provisioned rate. Once the CCER exceeds approximately 20%, the CER reaches 0.3% and above, and the throughput drops below 10 Mbps. Since both ratios move together, this experiment cannot separate their individual effects on throughput. Nevertheless, it has a practical consequence: a carrier that reports a non-negligible CCER is very likely to also produce uncorrectable errors, so the CCER should be treated as an early warning of service degradation, not as harmless.

# Partial Service

Partial Service is a mechanism defined in DOCSIS 3.0 that allows the CMTS to stop using one of the bonded carriers of a CM when that carrier is unhealthy. The decision is made by the CMTS based on the status that the CM reports. In the downstream direction, a carrier is typically removed when the CM loses synchronization (i.e., QAM or FEC lock) on it. In our experiments, this only happened when the SNR of the carrier fell below approximately 25 dB.

The goal of Partial Service is to take impaired carriers out of the bonding group, so that their CER and CCER stop degrading the TCP throughput. However, a carrier only enters Partial Service under very strong noise or interference. Before that point, it can operate for a long time with a moderate SNR and a high CER/CCER, which is precisely the condition that hurts throughput the most.

The following figures show this behaviour. In both experiments, the CM uses a 20-channel bonding group, and we inject interference on one carrier (771 MHz, Fig. A) or on two carriers (771 and 777 MHz, Fig. B). The green line is the TCP throughput (left axis), and the dots are the SNR of each carrier (right axis). The grey dots correspond to the carriers without interference.

**Fig. A.** 20-channel bonding, interference on one carrier (771 MHz).

![TCP throughput and per-carrier SNR over time, 20-channel bonding with interference on the 771 MHz carrier](/internet/PartialService/interferencia1CH-1.png)

In Fig. A, the SNR of the 771 MHz carrier drops from about 30 dB to about 26 dB within the first 900 s and then remains around that value. During that period, the carrier is still in use and the throughput falls well below the provisioned 50 Mbps, down to about 5 Mbps between 2500 s and 3600 s. After approximately 4400 s, the SNR falls below 25 dB, the carrier enters Partial Service, and the throughput largely recovers.

**Fig. B.** 20-channel bonding, interference on two carriers (771 and 777 MHz).

![TCP throughput and per-carrier SNR over time, 20-channel bonding with interference on the 771 MHz and 777 MHz carriers](/internet/PartialService/interferencia2CH-1.png)

Fig. B shows the same pattern. While both impaired carriers stay around 26 dB, the throughput drops to 20–30 Mbps (before 900 s) and to about 2–5 Mbps (after 1600 s). Between approximately 1000 s and 1600 s, the SNR of the 771 MHz carrier falls below 25 dB, that carrier is removed, and the throughput recovers to the provisioned rate. Interestingly, the throughput after 1600 s is lower than in the comparable period of Fig. A, which is consistent with the model: two impaired carriers expose roughly twice as many packets to codeword errors.

## Resulting throughput

In summary, TCP throughput in DOCSIS 3.0 becomes more resilient as the number of bonded carriers increases, i.e., a given CER on one carrier has less impact on a larger bonding group. The table below uses the model to estimate the maximum CER on a single impaired carrier that still allows a given throughput, for different bonding configurations ($$MSS = 1460$$ bytes, $$RTT = 27.5$$ ms).

| Target throughput (Mbps) | Max. CER, 8-channel bonding (%) | Max. CER, 16-channel bonding (%) | Max. CER, 24-channel bonding (%) |
| ---: | ---: | ---: | ---: |
| 6 | 0.573 | 1.145 | 1.718 |
| 12 | 0.143 | 0.286 | 0.430 |
| 24 | 0.036 | 0.072 | 0.107 |
| 50 | 0.008 | 0.016 | 0.025 |
| 100 | 0.002 | 0.004 | 0.006 |

For instance, to sustain 50 Mbps with 8 bonded channels, the impaired carrier must keep its CER below 0.008%, whereas with 24 channels a CER of up to 0.025% is tolerable. Since the model is optimistic compared with our measurements, these values should be read as upper bounds.

Finally, the CER and CCER of an impaired carrier degrade the throughput for as long as that carrier remains in the bonding group. Once it enters Partial Service, the throughput recovers, at the cost of losing that carrier's share of the bonding group capacity. In our experiments, a carrier only entered Partial Service when its SNR dropped below approximately 25 dB. Hence, in practice, the most harmful situation is not a carrier with a very poor SNR, but one with a moderately degraded SNR (around 26 dB in our tests) that is still in use.
