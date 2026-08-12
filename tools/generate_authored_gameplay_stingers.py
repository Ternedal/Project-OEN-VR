#!/usr/bin/env python3
"""Generate Project OEN's original gameplay-feedback + stinger audio pack.

No third-party samples are used. Short feedback cues are mono; stingers are stereo.
All output is 48 kHz / 24-bit PCM WAV with a -3 dBFS peak ceiling.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import math
import random
import shutil
import wave
import zipfile
from pathlib import Path

SR = 48_000
PEAK = 10 ** (-3 / 20)

COUNTS = {
    "SFX_INT_Place_Valid": 6,
    "SFX_INT_Place_Invalid": 4,
    "SFX_INT_Objective_Complete": 4,
    "SFX_INT_Discovery": 6,
    "SFX_INT_Danger_Warning": 4,
    "SFX_INT_Resource_Depleted": 4,
    "SFX_CRF_Start": 6,
    "SFX_CRF_Progress": 8,
    "SFX_CRF_Success": 6,
    "SFX_CRF_Fail": 5,
    "STG_Discovery_Small": 4,
    "STG_Objective_Major": 3,
    "STG_Danger_Reveal": 3,
    "STG_Signal_Success": 3,
}

STEREO_EVENTS = {
    "STG_Discovery_Small",
    "STG_Objective_Major",
    "STG_Danger_Reveal",
    "STG_Signal_Success",
}

def osc(freq: float, t: float, phase: float = 0.0) -> float:
    return math.sin(2.0 * math.pi * freq * t + phase)

def env(i: int, n: int, attack: float = 0.004, release: float = 0.08) -> float:
    t = i / SR
    d = n / SR
    a = min(1.0, t / max(attack, 1e-6))
    r = min(1.0, max(0.0, d - t) / max(release, 1e-6))
    return (a * a) * (r * r)

def lp_noise(n: int, rng: random.Random, alpha: float = 0.08) -> list[float]:
    y = 0.0
    out = []
    for _ in range(n):
        x = rng.uniform(-1.0, 1.0)
        y += alpha * (x - y)
        out.append(y)
    return out

def hp_noise(n: int, rng: random.Random, alpha: float = 0.035) -> list[float]:
    low = 0.0
    out = []
    for _ in range(n):
        x = rng.uniform(-1.0, 1.0)
        low += alpha * (x - low)
        out.append(x - low)
    return out

def normalize_mono(samples: list[float]) -> list[float]:
    mx = max((abs(x) for x in samples), default=1e-9)
    gain = PEAK / max(mx, 1e-9)
    return [max(-1.0, min(1.0, x * gain)) for x in samples]

def normalize_stereo(samples: list[tuple[float, float]]) -> list[tuple[float, float]]:
    mx = max((max(abs(l), abs(r)) for l, r in samples), default=1e-9)
    gain = PEAK / max(mx, 1e-9)
    return [(max(-1.0, min(1.0, l * gain)), max(-1.0, min(1.0, r * gain))) for l, r in samples]

def _pcm24(value: float) -> bytes:
    v = int(max(-1.0, min(1.0, value)) * ((1 << 23) - 1))
    if v < 0:
        v = (1 << 24) + v
    return bytes((v & 0xFF, (v >> 8) & 0xFF, (v >> 16) & 0xFF))

def write_mono(path: Path, samples: list[float]) -> None:
    frames = bytearray()
    for s in normalize_mono(samples):
        frames.extend(_pcm24(s))
    with wave.open(str(path), "wb") as w:
        w.setnchannels(1)
        w.setsampwidth(3)
        w.setframerate(SR)
        w.writeframes(frames)

def write_stereo(path: Path, samples: list[tuple[float, float]]) -> None:
    frames = bytearray()
    for l, r in normalize_stereo(samples):
        frames.extend(_pcm24(l))
        frames.extend(_pcm24(r))
    with wave.open(str(path), "wb") as w:
        w.setnchannels(2)
        w.setsampwidth(3)
        w.setframerate(SR)
        w.writeframes(frames)

def seed_for(kind: str, variant: int) -> int:
    return 7000 + variant * 131 + sum((i + 1) * ord(c) for i, c in enumerate(kind))

def synth_feedback(kind: str, variant: int) -> list[float]:
    rng = random.Random(seed_for(kind, variant))

    if kind == "SFX_INT_Place_Valid":
        d = 0.18 + rng.uniform(-0.015, 0.02); n = int(d * SR)
        f0, f1 = 350 + rng.uniform(-15,15), 590 + rng.uniform(-20,20)
        return [env(i,n,0.002,0.08)*(0.72*osc(f0+(f1-f0)*(i/n),i/SR)+0.18*osc((f0+f1)*0.75,i/SR)) for i in range(n)]

    if kind == "SFX_INT_Place_Invalid":
        d = 0.23 + rng.uniform(-0.02,0.02); n = int(d*SR)
        noise = lp_noise(n,rng,0.12)
        freq = 165 + rng.uniform(-4, 4)
        return [env(i,n,0.002,0.10)*(0.68*osc(freq,i/SR)+0.24*noise[i]) for i in range(n)]

    if kind == "SFX_INT_Objective_Complete":
        d = 0.65 + rng.uniform(-0.04,0.05); n = int(d*SR)
        freqs = [330, 495, 660]
        detune = [1 + rng.uniform(-0.006, 0.006) for _ in freqs]
        return [env(i,n,0.006,0.18)*sum((0.38/(j+1))*osc(f*detune[j],i/SR,0.3*j) for j,f in enumerate(freqs)) for i in range(n)]

    if kind == "SFX_INT_Discovery":
        d = 0.43 + rng.uniform(-0.03,0.04); n = int(d*SR)
        noise = hp_noise(n,rng,0.055)
        return [env(i,n,0.01,0.15)*(0.45*noise[i]+0.38*osc(740+260*(i/n),i/SR)) for i in range(n)]

    if kind == "SFX_INT_Danger_Warning":
        d = 0.52 + rng.uniform(-0.03,0.04); n = int(d*SR)
        out=[]
        for i in range(n):
            t=i/SR
            pulse = 0.35 + 0.65*(1 if int(t/0.09)%2==0 else 0.38)
            out.append(env(i,n,0.003,0.14)*pulse*(0.72*osc(118,t)+0.24*osc(177,t)))
        return out

    if kind == "SFX_INT_Resource_Depleted":
        d = 0.34 + rng.uniform(-0.025,0.03); n = int(d*SR)
        return [env(i,n,0.002,0.15)*(0.65*osc(360-190*(i/n),i/SR)+0.18*osc(720-380*(i/n),i/SR)) for i in range(n)]

    if kind == "SFX_CRF_Start":
        d = 0.22 + rng.uniform(-0.015,0.02); n=int(d*SR)
        noise=hp_noise(n,rng,0.08)
        return [env(i,n,0.002,0.09)*(0.42*noise[i]+0.52*osc(245+80*(i/n),i/SR)) for i in range(n)]

    if kind == "SFX_CRF_Progress":
        d = 0.12 + rng.uniform(-0.008,0.012); n=int(d*SR)
        f=510+rng.uniform(-35,35)
        return [env(i,n,0.001,0.06)*(0.76*osc(f,i/SR)+0.16*osc(f*1.99,i/SR)) for i in range(n)]

    if kind == "SFX_CRF_Success":
        d = 0.48 + rng.uniform(-0.025,0.04); n=int(d*SR)
        f0=300+rng.uniform(-10,10)
        return [env(i,n,0.003,0.16)*(0.55*osc(f0,i/SR)+0.32*osc(f0*1.5,i/SR)+0.15*osc(f0*2,i/SR)) for i in range(n)]

    if kind == "SFX_CRF_Fail":
        d = 0.42 + rng.uniform(-0.03,0.03); n=int(d*SR)
        noise=lp_noise(n,rng,0.06)
        return [env(i,n,0.003,0.15)*(0.54*osc(205-55*(i/n),i/SR)+0.35*noise[i]) for i in range(n)]

    raise ValueError(kind)

def chord(freqs, t, weights=None):
    if weights is None:
        weights = [1.0/(i+1) for i in range(len(freqs))]
    return sum(w*osc(f,t,0.15*i) for i,(f,w) in enumerate(zip(freqs,weights)))

def synth_stinger(kind: str, variant: int) -> list[tuple[float,float]]:
    rng = random.Random(seed_for(kind, variant))
    durations = {
        "STG_Discovery_Small": 1.55,
        "STG_Objective_Major": 3.2,
        "STG_Danger_Reveal": 2.35,
        "STG_Signal_Success": 4.1,
    }
    d = durations[kind] + rng.uniform(-0.08, 0.1)
    n = int(d*SR)
    left_noise = hp_noise(n,rng,0.025)
    right_noise = hp_noise(n,random.Random(seed_for(kind,variant)+991),0.025)

    if kind == "STG_Discovery_Small":
        base = 392 * (1 + rng.uniform(-0.004, 0.004))
    elif kind == "STG_Objective_Major":
        base = 196 * (1 + rng.uniform(-0.003, 0.003))
    elif kind == "STG_Danger_Reveal":
        base = 110 * (1 + rng.uniform(-0.002, 0.002))
    else:
        base = 261.63 * (1 + rng.uniform(-0.003, 0.003))

    out=[]
    for i in range(n):
        t=i/SR; p=i/n
        e=env(i,n,0.02,0.35)
        if kind == "STG_Discovery_Small":
            tonal=chord([base,base*1.5,base*2.0],t,[0.55,0.28,0.13])*(0.65+0.35*p)
            shimmer=0.12*math.sin(math.pi*p)*left_noise[i]
        elif kind == "STG_Objective_Major":
            rise=1+0.22*(p**1.5)
            tonal=chord([base*rise,base*1.5*rise,base*2*rise,base*2.5*rise],t,[0.5,0.28,0.18,0.08])
            shimmer=0.09*math.sin(math.pi*p)*left_noise[i]
        elif kind == "STG_Danger_Reveal":
            wob=1+0.018*math.sin(2*math.pi*2.2*t)
            tonal=chord([base*wob,base*1.414*wob,base*2*wob],t,[0.72,0.31,0.16])
            shimmer=0.16*(1-p)*left_noise[i]
        else:
            rise=1+0.18*p
            tonal=chord([base*rise,base*1.25*rise,base*1.5*rise,base*2*rise],t,[0.44,0.30,0.24,0.12])
            shimmer=0.11*math.sin(math.pi*p)*left_noise[i]
        pan=0.10*math.sin(2*math.pi*(0.22+0.03*variant)*t)
        l=e*((1-pan)*tonal + shimmer)
        r=e*((1+pan)*tonal + 0.11*math.sin(math.pi*p)*right_noise[i])
        out.append((l,r))
    return out

def generate(output: Path) -> dict:
    output.mkdir(parents=True, exist_ok=True)
    files=[]
    for event_id,count in COUNTS.items():
        for variant in range(1,count+1):
            name=f"{event_id}_{variant:02d}.wav"
            path=output/name
            if event_id in STEREO_EVENTS:
                write_stereo(path,synth_stinger(event_id,variant))
                channels=2
            else:
                write_mono(path,synth_feedback(event_id,variant))
                channels=1
            data=path.read_bytes()
            with wave.open(str(path),"rb") as w:
                duration=w.getnframes()/w.getframerate()
            files.append({
                "event_id":event_id,
                "variant":variant,
                "file":name,
                "channels":channels,
                "duration_seconds":round(duration,4),
                "bytes":len(data),
                "sha256":hashlib.sha256(data).hexdigest(),
            })
    metadata={
        "pack":"Project OEN authored gameplay + stingers v1",
        "sample_rate_hz":SR,
        "bit_depth":24,
        "peak_dbfs":-3.0,
        "generator":"tools/generate_authored_gameplay_stingers.py",
        "third_party_samples":False,
        "event_count":len(COUNTS),
        "file_count":len(files),
        "files":files,
    }
    (output/"pack_manifest.json").write_text(json.dumps(metadata,indent=2)+"\n",encoding="utf-8")
    (output/"LICENSE.txt").write_text(
        "Project OEN authored gameplay + stinger audio v1\n\n"
        "Original procedural works generated for Project OEN. No third-party samples are embedded.\n"
        "They may be used, modified and redistributed as part of Project OEN.\n",
        encoding="utf-8",
    )
    return metadata

def main() -> int:
    p=argparse.ArgumentParser()
    p.add_argument("--output",type=Path,default=Path("build/oen-authored-gameplay-stingers-v1"))
    p.add_argument("--zip",dest="zip_path",type=Path)
    p.add_argument("--clean",action="store_true")
    a=p.parse_args()
    if a.clean and a.output.exists():
        shutil.rmtree(a.output)
    meta=generate(a.output)
    if a.zip_path:
        a.zip_path.parent.mkdir(parents=True,exist_ok=True)
        with zipfile.ZipFile(a.zip_path,"w",compression=zipfile.ZIP_DEFLATED,compresslevel=9) as z:
            for path in sorted(a.output.iterdir()):
                z.write(path,arcname=path.name)
    print(f"Generated {meta['file_count']} WAV files across {meta['event_count']} events")
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
