---
title: "MOQT Foundations: From Session Setup to Object Delivery"
excerpt: "How a Media over QUIC publisher, relay, and subscriber establish sessions, select tracks on the control stream, and deliver objects on data streams, traced with moq-rs and draft-ietf-moq-transport-16."
layout: post
permalink: /video/moq-foundations/
categories: ["Video & Media"]
date: 2026-09-27 00:00:00 -0300
---

We approach Media over QUIC (MoQ) from broadcast multicast and HTTP Live Streaming (HLS) or Dynamic Adaptive Streaming over HTTP (DASH). HLS and DASH usually reach viewers through HTTP resources; managed Internet Protocol television (IPTV) often carries Real-time Transport Protocol (RTP) over User Datagram Protocol (UDP) multicast. This raises two immediate questions: where does MoQ sit in the stack, and who establishes a session with whom? Questions about captions, catalogs, signaling, packet loss, and media packaging follow from those basics.

We examine these questions through small use cases and implementation traces. This first installment follows connection establishment and the first object flow in a publisher–relay–subscriber deployment. We use `draft-ietf-moq-transport-16` (called **MOQT** here) as the protocol reference and the draft-16 [Cloudflare `moq-rs` implementation](https://github.com/cloudflare/moq-rs) as the concrete example. MoQ names the broader IETF effort; MOQT is its transport protocol. We first establish the roles and naming model, then read the setup, control, and data exchanges. Later installments can compare `moq-dev`, `moq-rs`, and `moqtail` and examine the questions outside this case.

## 1.1 MOQ Motivations

The distribution approaches familiar from broadcast make different trade-offs. HLS and DASH scale through HTTP caches, but live latency depends on how quickly segments or parts are published and how much the player buffers; low-latency HLS narrows that delay without removing the trade-off ([Apple's Low-Latency HLS guide](https://developer.apple.com/documentation/http-live-streaming/enabling-low-latency-http-live-streaming-hls)). WebRTC supports interactive latency, while distribution to a large audience commonly adds selective forwarding units (SFUs) and per-session forwarding state ([RFC 7667 §3.7](https://www.rfc-editor.org/rfc/rfc7667#section-3.7)). Managed Internet Protocol (IP) multicast efficiently replicates one flow to many receivers, but a multicast tree cannot adapt its sending rate to each receiver; loss handling and receiver differences need additional design ([RFC 8085 §4.1](https://www.rfc-editor.org/rfc/rfc8085#section-4.1)).

We find MoQ interesting because it proposes a standardized relay overlay where subscribers request named tracks and relays can aggregate demand and cache individual objects [draft-16 §2.2] [draft-16 §8.4]. This could offer a different balance between latency and scale. The table and Figure 1.1 compare what each intermediary handles; they do not rank measured performance. Our connection-establishment case measures neither latency nor scale, so those properties remain open for later study.

| Approach | What the intermediary handles | Strength | Main constraint for this comparison |
|---|---|---|---|
| HLS / DASH | HTTP media resources, such as segments or partial segments | Widely cacheable distribution to large audiences | Live delay depends on publication cadence and playback buffering. |
| WebRTC | Media streams forwarded through SFUs | Interactive delivery | Large audiences require a forwarding topology and per-session resources. |
| Managed IP multicast | Network replication of one packet flow | Efficient one-to-many delivery within a multicast-enabled network | Per-receiver adaptation and loss handling need additional mechanisms. |
| MoQ / MOQT | Named tracks and object metadata at a relay | Subscription aggregation and optional object caching | Its latency and scale in a deployment must be measured. |

![Distribution models considered in this guide](/video/moq-foundations/ch1-delivery-models.svg)

**Figure 1.1** — Four intermediaries and the information they use to distribute media. The drawing makes no measured performance claim.

### Reference architecture

To see how a subscriber reaches media through MoQ, we use three elements. A *track* is a named sequence of objects, and a *namespace* groups related track names; the next section defines the full hierarchy.

- **Original publisher:** produces the objects of a track and announces the namespace under which the track can be found.
- **Relay:** accepts separate sessions from publisher and subscriber, subscribes upstream when needed, and forwards objects downstream. It may cache objects.
- **End subscriber:** requests a track and receives its objects through the relay.

Publisher and subscriber are roles relative to a particular track, not fixed kinds of machine: a relay is a subscriber upstream and a publisher downstream [draft-16 §1.2]. In this deployment, the original publisher and end subscriber each initiate a session toward the relay, which acts as the server for both.

![Elements and sessions of the reference deployment](/video/moq-foundations/ch1-elements-and-sessions.svg)

**Figure 1.2** — Solid arrows show each client initiating a separate session toward the relay; dashed arrows show object delivery from publisher through relay to subscriber.

Figure 1.2 separates session initiation from object delivery. The subscriber initiates toward the relay even though the objects travel toward the subscriber. To follow its request, we first need the MOQT naming hierarchy.

## 1.2 The MOQT data model

MOQT names media without prescribing its codec or container. Throughout this chapter, `/bbb` is a sample namespace and `1.m4s` is its video track in the `moq-rs` deployment described next. A **Track Namespace** groups related track names for publication and discovery. A **Full Track Name** is the namespace plus one **Track Name**, such as `/bbb` plus `1.m4s` in this deployment. We write this pair as `(/bbb, 1.m4s)` for clarity; the parentheses are explanatory notation, not a URL or a wire encoding. A **track** is a sequence of groups and the target of a subscription.

Each **group** contains objects and provides a possible join point. Within a group, objects may be arranged into **subgroups** whose dependency and priority relationships make sense on one stream. An **object** is the addressable unit: its payload is application-defined bytes and its content cannot change after publication [draft-16 §2.1] [draft-16 §2.2] [draft-16 §2.3] [draft-16 §2.4.1].

| Element | Meaning | Example in this guide |
|---|---|---|
| Track Namespace | Shared naming prefix | `/bbb` |
| Track Name | Name of one track within the namespace | `1.m4s` (video), `2.m4s` (audio), or `.catalog` |
| Full Track Name | Namespace and Track Name together; the subscription target | `(/bbb, 1.m4s)` |
| Track | Sequence of groups identified by a Full Track Name | The video sequence named `(/bbb, 1.m4s)` |
| Group | Collection of objects and a potential join point | A coded sequence in the draft's video example |
| Subgroup | Objects from one group arranged for stream delivery | One temporal layer in the draft's example |
| Object | Addressable payload plus transport metadata | One video frame in the draft's example |

The video mappings in the last three rows are **examples**, not definitions of MOQT. A track need not be a resolution, a group need not be a group of pictures (GOP), and an object need not be a frame. The application chooses the packaging. In particular, `moq-rs` also puts initialization data and a catalog into MOQT objects. This hierarchy explains the two channels that appear later: control messages select named tracks, while data streams carry their objects. A `Track Alias` is a compact, session-local identifier used on data delivery after a subscription is accepted [draft-16 §10.1].

![The MOQT data model](/video/moq-foundations/ch1-object-model-decisions.svg)

**Figure 1.3** — An illustrative video mapping shows the named track, two groups, and alternative ways to deliver their objects. The grouping is an example from the draft, not a measurement of this deployment.

Figure 1.3 follows a track into groups, subgroups, and objects. Its alternative delivery paths show why MOQT defines these units separately; they do not describe the media packaging observed below.

An HTTP cache can obtain an uncached file from an upstream cache or origin, then serve later requests locally. MoQ has a similar demand-driven shape, but a subscriber requests a Full Track Name rather than a file. The track is the requested live sequence; if a relay caches, the individual objects are identified by Full Track Name, Group ID, and Object ID [draft-16 §2.4.1] [draft-16 §8.1] [draft-16 §8.4]. A relay can aggregate downstream interest into an upstream subscription, but caching is optional. With only one subscriber in this case, we can observe the upstream request, not aggregation across subscribers or a cache hit.

## 1.3 A small `moq-rs` deployment

The reference deployment has one publisher, one relay, one subscriber, and one video rendition. The publisher uses the namespace `/bbb` for the Big Buck Bunny sample. It offers two media tracks, `1.m4s` (video) and `2.m4s` (audio), plus an initialization track `0.mp4` and a `.catalog` track. We consider two subscriber request sequences using this architecture: one requests the initialization and media tracks, while the other explicitly requests the catalog first. These names and the Common Media Application Format (CMAF) packaging are `moq-rs` choices, not MOQT naming rules. The example clients and relay are provided by the [`moq-rs` repository](https://github.com/cloudflare/moq-rs); its README describes them as development examples.

For `/bbb`, the relay accepts a subscriber's request for a track and issues its own request to the publisher. The subscriptions have independent identifiers and responses because they belong to different sessions. The trace below makes that mapping visible.

The relay in this deployment listens on port `4443`:

```js
INFO moq_relay_ietf::relay: listening on [::]:4443
```

The publisher prepares the sample under its namespace, and the subscriber requests it from the relay:

```js
ffmpeg ... | moq-pub --name bbb <relay-hostname>
moq-sub --name bbb "$RELAY" | ffplay -
```

These commands are schematic, not a copy-and-paste runbook: `<relay-hostname>` is the relay's DNS name, `$RELAY` is its HTTPS URL on port `4443`, `ffmpeg` feeds the publisher, and `ffplay` plays the subscriber's output. Once the relay is listening, the publisher has connected and announced `/bbb`, and the subscriber has connected and subscribed, there is an end-to-end delivery path. The publisher's announcement alone does not mean that the relay is already receiving the media objects.

The input MP4 contains two encoded streams:

| Source stream | Codec | Characteristics |
|---|---|---|
| Video | H.264 | 1280×720; 24 frames per second |
| Audio | AAC | Stereo; 44.1 kHz sample rate |

The publisher wrapper copies these streams into CMAF-style fragmented MP4. FFmpeg's [`separate_moof` and `frag_every_frame` options](https://ffmpeg.org/ffmpeg-formats.html) produce separate video and audio fragments, with one encoded video frame or AAC frame per fragment in this run. As Figure 1.4 shows, the initialization boxes (`ftyp` and `moov`) describe the file and its tracks; in each media fragment, `moof` describes the coded sample and `mdat` holds its encoded bytes. The publisher places these units into MOQT objects, as we examine in §1.6.

![Fragmented MP4 and MOQT objects in the reference deployment](/video/moq-foundations/ch1-cmaf-object-mapping.svg)

**Figure 1.4** — In this run, the initialization boxes form one object; each video or audio `moof`/`mdat` pair forms another. The encoded video frame or AAC frame is carried in `mdat`, not `moof`.

## 1.4 Session establishment and flow direction

Session setup crosses several protocol boundaries, which Figure 1.5 separates before we read the trace. IP and UDP carry QUIC packets. QUIC establishes the secure connection and supplies independent streams. In this `moq-rs` deployment, HTTP/3 runs over QUIC, and an HTTP extended `CONNECT` establishes a WebTransport session. MOQT uses that session's streams for its own setup, subscriptions, and objects [draft-16 §3.1.1] [draft-16 §3.3]. MOQT and HTTP/3 both operate at the application layer, but they have different roles here: MOQT defines the media delivery protocol, while HTTP/3 helps establish its WebTransport carrier. MOQT can also run directly over QUIC [draft-16 §3.1.2].

![Protocol stack used by the moq-rs example](/video/moq-foundations/ch1-protocol-stack.svg)

**Figure 1.5** — MOQT and HTTP/3 occupy the application layer but serve different purposes. The WebTransport session carries MOQT streams; HTTP/3 establishes that session over QUIC, UDP, and IP.

Both clients initiate toward the relay. This leaves the reachability requirement at the relay in the simple deployment: it needs an address the two clients can contact, while the clients may be behind network address translation (NAT). Figure 1.6 separates the directions into two rows: the subscriber initiates toward the relay although objects arrive from it. A larger overlay can add relays, but their routing and initiation choices need their own design; this case has only one relay.

![Initiation and flow direction](/video/moq-foundations/ch1-initiation-and-flow.svg)

**Figure 1.6** — Session initiation converges on the relay; media flows from publisher to subscriber.

In the relay trace for this deployment, the publisher's QUIC connection and WebTransport session are established first. The publisher opens MOQT's bidirectional control stream and exchanges `CLIENT_SETUP` and `SERVER_SETUP`. Only after that setup does it advertise the Track Namespace `/bbb` with `PUBLISH_NAMESPACE`; this advertises available tracks under `/bbb`, not a particular Full Track Name. The subscriber then establishes a **separate** connection and WebTransport session, completes its own MOQT setup, and requests a specific track. MOQT calls the underlying carrier a *Transport Session*: it can be a raw QUIC connection or a WebTransport session. One MOQT session is established on that carrier in this example [draft-16 §1.2] [draft-16 §3.1] [draft-16 §3.3] [draft-16 §9.20].

The publisher can announce a namespace before anyone subscribes. Here the relay registers `/bbb` and waits; when a subscriber requests a Full Track Name within that namespace, it originates an upstream subscription for the same track and delivery begins. The session, namespace advertisement, and track subscription are therefore separate steps. This is the demand-driven behavior described in §1.1. If a subscriber arrives before the publisher, MOQT has a separate namespace-discovery mechanism for interest in a prefix [draft-16 §6.1]; that mechanism is outside this case.

## 1.5 The control stream

MOQT's first stream is client-initiated and bidirectional. Its setup exchange establishes the MOQT session, and the stream stays open for the session's lifetime [draft-16 §3.3]. It then carries requests, confirmations, and later changes in subscription state. A `SUBSCRIBE` request can express a starting point, filter, and priority; `SUBSCRIBE_OK` confirms it and supplies the Track Alias [draft-16 §9.9] [draft-16 §9.10]. In this guide, **control channel** means that single stream; **data channel** means the collection of streams carrying objects. MOQT also uses another kind of bidirectional stream for namespace subscription, which this case does not exercise [draft-16 §3.3].

The following bounded excerpt is from the relay trace of the reference deployment. Timestamps and logging prefixes have been removed, and ellipses mark omitted fields; the displayed message types and fields are unchanged. It shows the publisher's WebTransport and MOQT setup, followed by the namespace request:

```js
// Publisher related control messages logs in the relay
web_transport_quinn::settings: sending SETTINGS frame settings=Settings({...})
web_transport_quinn::settings: received SETTINGS frame settings=Settings({...})
web_transport_quinn::connect: received CONNECT request request=ConnectRequest { ... protocols: ["moqt-16"], ... }
web_transport_quinn::connect: sending CONNECT response response=ConnectResponse { status: 200, protocol: Some("moqt-16") }
moq_transport::control: MoQT control message direction="recv" msg_type="CLIENT_SETUP"
moq_transport::control: MoQT control message direction="sent" msg_type="SERVER_SETUP"
moq_transport::control: MoQT control message direction="recv" msg_type="PUBLISH_NAMESPACE" request_id=0 namespace=/bbb
moq_transport::control: MoQT control message direction="sent" msg_type="REQUEST_OK" request_id=0
```

The `web_transport_quinn` lines belong to HTTP/3/WebTransport setup using the Quinn QUIC implementation. `SETTINGS` advertises capabilities; the successful `CONNECT` creates the WebTransport session and selects `moqt-16`. Only then do the `moq_transport` lines show MOQT's own setup. `PUBLISH_NAMESPACE` tells the relay that this publisher can serve the Track Namespace `/bbb`; `REQUEST_OK` confirms that request. The message contains no Track Name, so it does not identify a video, audio, or catalog track. The shared `request_id=0` pairs request and response. The relay can keep multiple requests in flight and match their responses by identifier, independent of arrival order [draft-16 §3.1.1] [draft-16 §9.1] [draft-16 §9.20].

The subscriber follows the same lower-layer setup, then sends `SUBSCRIBE`. The next excerpt is from the same relay trace; `recv` and `sent` are from the **relay's** point of view. The first two requests are for the initialization track, and the later requests follow the same pattern for video and audio:

```js
// Suscriber related control messages logs in the relay
moq_transport::control: MoQT control message direction="recv" msg_type="SUBSCRIBE" subscribe_id=0 namespace=/bbb track_name=0.mp4
moq_transport::control: MoQT control message direction="sent" msg_type="SUBSCRIBE" subscribe_id=1 namespace=/bbb track_name=0.mp4
moq_transport::control: MoQT control message direction="recv" msg_type="SUBSCRIBE_OK" subscribe_id=1 track_alias=1
moq_transport::control: MoQT control message direction="sent" msg_type="SUBSCRIBE_OK" subscribe_id=0 track_alias=0
moq_transport::control: MoQT control message direction="recv" msg_type="SUBSCRIBE" subscribe_id=2 namespace=/bbb track_name=1.m4s
moq_transport::control: MoQT control message direction="sent" msg_type="SUBSCRIBE" subscribe_id=3 namespace=/bbb track_name=1.m4s
moq_transport::control: MoQT control message direction="recv" msg_type="SUBSCRIBE" subscribe_id=4 namespace=/bbb track_name=2.m4s
moq_transport::control: MoQT control message direction="sent" msg_type="SUBSCRIBE" subscribe_id=5 namespace=/bbb track_name=2.m4s
moq_transport::control: MoQT control message direction="recv" msg_type="SUBSCRIBE_OK" subscribe_id=3 track_alias=3
moq_transport::control: MoQT control message direction="sent" msg_type="SUBSCRIBE_OK" subscribe_id=2 track_alias=2
```

Each `SUBSCRIBE` carries a Track Namespace and a Track Name. In the first line, `/bbb` and `0.mp4` together form the Full Track Name `(/bbb, 0.mp4)`: the subscriber asks for that track, not for the whole namespace. The relay sends its own `SUBSCRIBE` for the **same Full Track Name** toward the publisher. Figure 1.7 places these requests on separate sessions. The downstream request uses ID `0` and receives alias `0`; the upstream request uses ID `1` and receives alias `1`.

Likewise, `(/bbb, 1.m4s)` uses request ID `2` and alias `2` downstream, but ID `3` and alias `3` upstream. The log calls the request identifier `subscribe_id`; the draft calls it a Request ID. These IDs pair each `SUBSCRIBE` with its `SUBSCRIBE_OK`, while Track Aliases identify tracks on data streams. Both are local to their session; the Full Track Name remains the same across the relay's two requests [draft-16 §2.4.1] [draft-16 §9.1] [draft-16 §9.9] [draft-16 §9.10] [draft-16 §10.1]. The relay thus acts as a subscriber on its publisher-facing session and as a publisher on its subscriber-facing session, as described in §1.1. The audio confirmation is omitted for brevity.

Notice that the first track requested by the suscriber is `track_name=0.mp4`. The choice to ask for `0.mp4` first is specific to this `moq-rs` media workflow: its fragmented MP4 (fMP4) initialization data lets the subscriber identify `1.m4s` as video and `2.m4s` as audio. Immediately after that subscription, the subscriber logs reports:

```js
moq_sub::media: using 1.m4s for video
moq_sub::media: using 2.m4s for audio
```

![Control exchange across the two sessions](/video/moq-foundations/ch1-control-sequence.svg)

**Figure 1.7** — The relay requests the same Full Track Name on a second session after the publisher has announced its namespace.

Alternatevely to using fragmented MP4 (fMP4) for initialization, `moq-rs` can use catalogs. A catalog can serve a discovery role analogous to a manifest in HLS or DASH: it describes available tracks and information a client can use to choose among them. MOQT itself does not require the `moq-rs` names or prescribe a universal catalog track. In this implementation, the publisher also offers `.catalog`. On the catalog-first path, the subscriber requests Full Track Name `(/bbb, .catalog)` first. On `moq-rs`, using `.catalog` or `0.mp4` is a suscriber choise:

```js
moq_transport::control: MoQT control message direction="recv" msg_type="SUBSCRIBE" subscribe_id=0 namespace=/bbb track_name=.catalog
moq_transport::control: MoQT control message direction="sent" msg_type="SUBSCRIBE" subscribe_id=1 namespace=/bbb track_name=.catalog
moq_transport::control: MoQT control message direction="recv" msg_type="SUBSCRIBE_OK" subscribe_id=1 track_alias=1
moq_transport::control: MoQT control message direction="sent" msg_type="SUBSCRIBE_OK" subscribe_id=0 track_alias=0
```

Take into account that the control stream carries the Full Track Name in `SUBSCRIBE` only, either for `.catalog` or `0.mp4`, not the catalog payload or init data. The actual information  is delivered as any other track trough a data stream.

## 1.6 The data streams

After a subscription is accepted, objects can move on unidirectional streams. In the common **subgroup** forwarding mode used here, a stream begins with a `SUBGROUP_HEADER` identifying the Track Alias, Group ID, and Subgroup ID, then carries one or more objects [draft-16 §3.3] [draft-16 §10.4.2]. The control response establishes the alias that the data-stream header uses in place of repeating the Full Track Name [draft-16 §10.1]. MOQT also defines object datagrams and fetch streams; this case follows subscribed subgroup streams [draft-16 §10].

Within a group, a **subgroup** is a sequence of one or more objects in ascending Object ID order. The original publisher assigns its Subgroup ID, and subscribed objects in that subgroup normally share one stream [draft-16 §2.2]. An **object** is the addressable unit identified by Full Track Name, Group ID, and Object ID; its payload is opaque to MOQT [draft-16 §2.1]. The video group observed below contains one subgroup. The mapping from video frames to its objects is chosen by the publisher, not prescribed by MOQT.

### Track payloads and the initialization path

The publisher exposes four tracks under `/bbb`. Their names describe ongoing MOQT tracks, not downloadable `.mp4` or `.m4s` files. The catalog is a separate application description, not part of the MP4 initialization data:

| Track role | Full Track Name | Objects carried in this deployment |
|---|---|---|
| Initialization | `(/bbb, 0.mp4)` | One object with `ftyp` and `moov`: format and track metadata needed before decoding the media. |
| Video | `(/bbb, 1.m4s)` | Successive `moof`/`mdat` pairs, one coded video frame per object in this run. |
| Audio | `(/bbb, 2.m4s)` | Successive `moof`/`mdat` pairs, one AAC frame (one MP4 sample) per object in this run. |
| Catalog | `(/bbb, .catalog)` | An application JSON object describing available tracks; requested on the catalog-first path below. |

The initialization-first subscriber requests `0.mp4` before the video and audio tracks. In the [publisher's media parser](https://github.com/cloudflare/moq-rs/blob/main/moq-pub/src/media.rs), each `moof`/`mdat` pair becomes one MOQT object. A pair is a **CMAF chunk** in the [CMSF draft's terminology](https://datatracker.ietf.org/doc/html/draft-ietf-moq-cmsf-01#section-3.3). The received MP4 confirms that each video pair in the interval below contains one coded sample. Unlike an HLS or DASH segment that may carry a whole GOP, this publisher delivers the video's frames as individually addressable MOQT objects while keeping them in a common group.

This mapping is a `moq-rs` packaging choice, not a requirement of MOQT draft-16: MOQT leaves encoding and packaging to MoQ Streaming Formats and treats object payloads as application-defined bytes [draft-16 §1] [draft-16 §2.1]. The choice lets the example accept FFmpeg's fragmented MP4 output and use an [existing compatible web player](https://github.com/cloudflare/moq-rs#interoperability); publishing one frame per fragment also makes frames individually addressable without waiting for a longer segment. This practical motivation follows from the example workflow and draft-16's goal of reusing existing packaging [draft-16 §1.1.3]; it is not a measured browser-compatibility result. Related drafts describe [MSF](https://datatracker.ietf.org/doc/draft-ietf-moq-msf/), its CMAF-based [CMSF](https://datatracker.ietf.org/doc/draft-ietf-moq-cmsf/) extension, and the [Low Overhead Media Container (LOC)](https://datatracker.ietf.org/doc/draft-ietf-moq-loc/). Draft-16 does not prescribe or enumerate these formats; a later experiment can compare them.

The following extract shows the first video group transmitted on the data channel in this run. The `SUBSCRIBE` line names `(/bbb, 1.m4s)`, the track the subscriber identifies as video from the initialization data (§1.5). `SUBSCRIBE_OK` assigns Track Alias `3`, which then appears in the subgroup header. Retained lines follow their original order in the publisher capture. Wall-clock timestamps, colors, and module prefixes are removed; ellipses mark omitted fields, intermediate video objects, and interleaved audio lines:

```js
moq_transport::control: MoQT control message direction="recv" msg_type="SUBSCRIBE" subscribe_id=3 namespace=/bbb track_name=1.m4s
moq_transport::control: MoQT control message direction="sent" msg_type="SUBSCRIBE_OK" subscribe_id=3 track_alias=3
[PUBLISHER] serve_subgroup: opened unidirectional stream
[PUBLISHER] serve_subgroup: sending header - track_alias=3, group_id=25, subgroup_id=Some(0), ...
[PUBLISHER] serve_subgroup: sending object #1 - object_id=0, ...
[PUBLISHER] serve_subgroup: sending object #2 - object_id=1, ...
...
[PUBLISHER] serve_subgroup: sending object #60 - object_id=59, ... payload_length=8236, ...
[PUBLISHER] serve_subgroup: completed subgroup (group_id=25, subgroup_id=0, 60 objects sent)
[PUBLISHER] serve_subgroup: sending header - track_alias=3, group_id=26, subgroup_id=Some(0), ...
[PUBLISHER] serve_subgroup: sending object #1 - object_id=0, ...
```

The first group sent after this subscription has Group ID `25` because the publisher was already processing the video and forming groups before the subscriber joined. This is the video track: `track_name=1.m4s` in `SUBSCRIBE` maps to `track_alias=3` in the header. Group `25` contains 60 objects, with Object IDs `0` through `59`; group `26` then begins at the next keyframe with Object ID `0` again. The `#1` and `#60` labels are log counters, while `object_id=` identifies the objects. The [publisher](https://github.com/cloudflare/moq-rs/blob/main/moq-pub/src/media.rs) starts a new group at each detected video keyframe. In this observed GOP, 60 video objects match 60 coded frames in the received MP4. Another GOP in the source need not have the same length, and MOQT itself requires neither one GOP per group nor one frame per object. Group IDs are assigned by the original publisher and scoped to a track [draft-16 §2.3.1]; the audio track's group `25` is separate.

The log also uses `payload chunk`, but that is a portion of an object's bytes written by this implementation, not a CMAF chunk or another MOQT unit. The first video object appears as one such portion in the publisher log and 74 in the relay data trace. Forwarding changed the write-buffer boundaries, not the one-frame, one-CMAF-chunk, one-object mapping observed here.

### Track payloads and the catalog path

We mentioned that the publisher delivers the catalog as an object on a separate data stream, using the same mechanism as the media track. The publisher produced the following catalog on the catalog path. It is the application's JSON content, with the timestamp and log prefix removed; it is **not** a MOQT control message:

```json
{
  "version": 1,
  "streamingFormat": 1,
  "streamingFormatVersion": "0.2",
  "supportsDeltaUpdates": true,
  "commonTrackFields": {
    "namespace": "/bbb",
    "packaging": "cmaf",
    "renderGroup": 1
  },
  "tracks": [
    {
      "name": "1.m4s",
      "initTrack": "0.mp4",
      "selectionParams": {
        "codec": "avc1.64001F",
        "width": 1280,
        "height": 720
      }
    },
    {
      "name": "2.m4s",
      "initTrack": "0.mp4",
      "selectionParams": {
        "codec": "mp4a.40.2",
        "bitrate": 129403,
        "samplerate": 44100,
        "channelConfig": "2"
      }
    }
  ]
}
```

The catalog pairs `commonTrackFields.namespace=/bbb` with the track names `1.m4s` and `2.m4s`, describing Full Track Names `(/bbb, 1.m4s)` and `(/bbb, 2.m4s)`. The first is a 1280×720 video track; the second is audio, and both refer to `0.mp4` as their initialization track. This `namespace` field is application JSON, not another `PUBLISH_NAMESPACE` control message. The `supportsDeltaUpdates` field advertises an application capability; this case does not exercise an update.

The publisher trace then shows what happens after the relay subscribes to `.catalog`. The excerpt removes timestamps, ANSI colors, and module prefixes, while retaining the recorded fields:

```js
[PUBLISHER] serve_subgroup: opened unidirectional stream
[PUBLISHER] serve_subgroup: sending header - track_alias=1, group_id=0, subgroup_id=Some(0), priority=0, header_type=SubgroupIdExt
[PUBLISHER] serve_subgroup: sending object #1 - object_id=0, object_id_delta=0, payload_length=618, status=None, extension_headers={  }
[PUBLISHER] serve_subgroup: completed subgroup (group_id=0, subgroup_id=0, 1 objects sent)
```

The trace records one unidirectional stream for group `0`, subgroup `0`, with one 618-byte catalog object. The preceding `SUBSCRIBE_OK` assigned alias `1` to `(/bbb, .catalog)` on the publisher-to-relay session, matching `track_alias=1` in this header. The downstream subscriber receives alias `0` for the same Full Track Name on its separate session. The media excerpt above shows the same delivery mechanism for `1.m4s`; corresponding trace lines also show objects on `0.mp4` and `2.m4s`. A catalog is therefore ordinary track data from MOQT's perspective, even though its content guides later subscription choices. Its format and the way a client discovers its name are application-level conventions. Neither request path is a universal MOQT rule.

![Control decisions and data delivery in the reference deployment](/video/moq-foundations/ch1-data-flow.svg)

**Figure 1.8** — Control requests select tracks; data streams carry the catalog, initialization, or media objects selected on each path.

Figure 1.8 brings the two paths together: a control request selects a track, while separate unidirectional streams carry its objects. This separation matters when packets are lost.

### Independent streams and head-of-line blocking

QUIC delivers bytes in order **within** a stream, but loss on one stream does not prevent another stream's available bytes from being delivered to the application. This avoids the connection-wide head-of-line blocking of the Transmission Control Protocol (TCP) ([RFC 9000 §2](https://www.rfc-editor.org/rfc/rfc9000.html#section-2)); it does not remove dependencies within a subgroup or the need to retransmit data an application still wants. The application decides how to group related objects. The draft's example places temporal video layers in different subgroups so less important layers can be delayed or abandoned without necessarily blocking the base layer [draft-16 §2.2].

The excerpts show `group_id`, `subgroup_id`, and opened unidirectional streams. They do **not** show a temporal-layer split or an abandoned stream. Figure 1.9 shows an illustrative packaging choice from the draft, not an observation from this deployment. A later congestion study could measure whether the implementation produces and discards such subgroups.

![Illustrative subgroup-to-stream mapping](/video/moq-foundations/ch1-subgroup-to-stream.svg)

**Figure 1.9** — An application may place different dependencies in separate subgroups and streams; this mapping is illustrative, not observed here.

### Control and data under congestion

When a data stream becomes too late or unhelpful, either endpoint may cancel it without cancelling the subscription or closing the MOQT session [draft-16 §10.4.1]. A completed subgroup stream ends with QUIC `FIN`; one stopped before all required objects are sent uses `RESET_STREAM` or `RESET_STREAM_AT`, so the receiver can distinguish completion from interruption [draft-16 §10.4.3]. The draft also requires the sender to allocate connection flow-control credit to the control stream before data streams, avoiding a deadlock in which the receiver is waiting for the alias-confirming control message [draft-16 §10.4.2].

Figure 1.10 illustrates this selective response to congestion while control state remains available. Whether the surviving media stays decodable depends on how the application packaged dependencies; MOQT does not guarantee that any arbitrary subgroup can be dropped safely. The traces here do not demonstrate congestion or a stream reset.

![State of each channel under a bandwidth reduction](/video/moq-foundations/ch1-channels-under-congestion.svg)

**Figure 1.10** — Conceptual response to congestion: one data stream can be interrupted while the control stream and subscription remain open.

## 1.7 Session lifecycle

Figure 1.11 puts the initialization-first path on a timeline. The relay listens, and the publisher establishes a session and announces `/bbb`. The subscriber then establishes a separate session and requests `(/bbb, 0.mp4)`, followed by `(/bbb, 1.m4s)` and `(/bbb, 2.m4s)`. Objects cross the relay only after those requests, although the publisher is already processing media. Both sessions eventually end. This order distinguishes **announcing availability** from **transmitting objects**: the relay registers the namespace before the first subscriber request and starts its upstream subscriptions only after that request.

| Stage | Control state | Data state |
|---|---|---|
| Relay listening | No MOQT session yet | No delivery |
| Publisher announced | Publisher session and `/bbb` registration active | No upstream subscription yet |
| Subscriber subscribed | Separate subscriber session; relay maps downstream and upstream requests | Requested objects cross the two sessions |
| Sessions ending | Subscriptions and namespace registration are released | Open streams complete or are interrupted |

When the subscriber leaves, its subscriptions cease; the publisher may still serve other subscribers. When the publisher leaves, the relay can no longer serve `/bbb` from this publisher and removes the namespace registration created after `PUBLISH_NAMESPACE`. This reverses the setup's state changes, although individual teardown messages depend on the termination path. MOQT permits termination at any point: direct QUIC uses `CONNECTION_CLOSE`, and WebTransport uses `CLOSE_WEBTRANSPORT_SESSION` [draft-16 §3.4].

| Termination path | What to expect | Observed here |
|---|---|---|
| Explicit close | The endpoint closes its transport session using the mechanism for its carrier. | Not demonstrated by the excerpts. |
| Timeout | The connection stops responding and the transport reports expiry. | Both sessions time out; the relay also records namespace deregistration. |

The relay records the end of the two sessions and removal of `/bbb` as follows. These lines retain the reported errors and namespace while omitting timestamps and other fields:

```js
moq_relay_ietf::relay: MoQ session error: webtransport error: session error: connection error: timed out
moq_relay_ietf::local: deregistering namespace route source from locals namespace=/bbb
moq_relay_ietf::relay: MoQ session error: webtransport error: session error: connection error: timed out
```

This shows timeout-driven teardown and namespace deregistration, not an acknowledged graceful departure.

![Timeline of both channels](/video/moq-foundations/ch1-channel-timeline.svg)

**Figure 1.11** — Conceptual session lifecycle. The observed teardown was timeout-driven.

## 1.8 Terminology, evidence, and outlook

| Term | Meaning in this chapter |
|---|---|
| MoQ | The broader IETF Media over QUIC effort. |
| MOQT | `draft-ietf-moq-transport`: session, control, and object delivery. |
| Transport Session | A raw QUIC connection or a WebTransport session [draft-16 §1.2]. |
| Control channel | This guide's shorthand for the MOQT control stream. |
| Data channel | This guide's shorthand for the unidirectional streams carrying subscribed objects. |
| Full Track Name | Track Namespace plus Track Name; the target of a subscription. |
| Track Alias | Compact identifier for a track in a particular session's data delivery. |
| Object | Addressable payload with metadata; the cached unit if a relay caches. |

These terms should not be substituted for neighboring formats' units. An HLS or DASH *segment* is an HTTP media resource; a MOQT track, group, and object have distinct naming and delivery roles. Here a *CMAF chunk* is one `moof`/`mdat` pair inside a media object, while a logged `payload chunk` is merely an implementation write-buffer portion (§1.6). Neither is a separate level of MOQT naming.

`[draft-16 §N]` refers to the [frozen `draft-ietf-moq-transport-16`](https://www.ietf.org/archive/id/draft-ietf-moq-transport-16.txt), dated 13 January 2026. Protocol rules come from that draft; the track names, command examples, and trace excerpts describe the `moq-rs` reference deployment above.

The setup, subscription, and teardown excerpts come from the relay capture, the media object excerpt from the publisher capture, and the track-selection excerpt from the subscriber capture, recorded on 22 September 2026. The catalog excerpts come from the catalog-request relay and publisher capture, recorded on 25 September 2026.

These source files are optional audit trails: the excerpts and their interpretation are included here. They are application and relay logs, not packet captures. Timestamps, logging prefixes, and other omissions are identified beside each excerpt. Figures marked illustrative show protocol possibilities rather than measured behavior.

Several neighboring names will recur in later installments. [WARP](https://datatracker.ietf.org/doc/draft-ietf-moq-warp/) was an earlier MoQ streaming-format draft, now superseded by [MSF](https://datatracker.ietf.org/doc/draft-ietf-moq-msf/); [LOC](https://datatracker.ietf.org/doc/draft-ietf-moq-loc/) defines a low-overhead media container. The [`moq-dev` project](https://github.com/moq-dev/moq) develops `moq-lite` as a separate transport approach and `hang` as its media layer. This chapter's observed messages belong to draft-16 MOQT in `moq-rs`.

We observe two separately established sessions, the same Full Track Name requested across them with different session-local IDs and aliases, and objects delivered on streams distinct from the control stream. The relay requests the track upstream only after downstream interest appears. These observations explain the connection path; they do not measure latency, scale, or behavior under congestion. Later chapters can examine setup from the first packet, message encoding, per-stream loss and priority, alternative packaging, catalog updates, relay chaining, quality switching, authorization, retrieval of older objects, and changes to an active subscription.
