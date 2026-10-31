# Proposed seed sources

From @adhibskr for @reiva5 to put into `sources.yaml` (owner's call). Checked on 31 Oct 2026: every URL below returned HTTP 200 to our honest `USER_AGENT`, and `robots.txt` allows it.

## Changes to the current `sources.yaml`

- **Remove `https://www.nia.or.th/`** and **`https://www.sginnovate.com/`**: their `robots.txt` disallows our crawler (rule 4, same as e27).
- **Replace the Cradle homepage** with the CIP Spark, CIP Sprint and grants pages below.
- **Keep** `mystartup.gov.my`, `mranti.my`, `nic.gov.vn`, `qboinnovation.com`, `tsc.gov.kh`, the Startup SG portal, and the regional and aggregator seeds. No better programme page was found for MyStartup or MRANTI; expect few records from them.
- **Needs the headless browser** (under 500 characters of text without it): `startupsg.gov.sg`, `nic.gov.vn`, `mdec.my`.

## Paste-ready list (30 seeds)

```yaml
sources:
  # Malaysia
  - {url: "https://www.mystartup.gov.my/", kind: portal, country: MY}
  - {url: "https://www.cradle.com.my/grants/", kind: portal, country: MY}
  - {url: "https://www.cradle.com.my/cip-spark/", kind: program, country: MY}
  - {url: "https://www.cradle.com.my/cip-sprint/", kind: program, country: MY}
  - {url: "https://mranti.my/", kind: portal, country: MY}
  - {url: "https://www.mdec.my/initiatives-grants", kind: portal, country: MY}

  # Singapore (headless browser)
  - {url: "https://www.startupsg.gov.sg/programmes/", kind: portal, country: SG}
  - {url: "https://www.startupsg.gov.sg/programmes/4894/startup-sg-founder", kind: program, country: SG}
  - {url: "https://www.startupsg.gov.sg/programmes/4895/startup-sg-tech", kind: program, country: SG}

  # Thailand
  - {url: "https://startupthailand.nia.or.th/", kind: portal, country: TH}
  - {url: "https://startupthailand.nia.or.th/ext/globalstartuphub/startup-thailand-2026-en.php", kind: program, country: TH}

  # Indonesia (Bahasa Indonesia)
  - {url: "https://ukmindonesia.id/baca-deskripsi-program/kementerian-umkm-buka-inkubasi-solusi-teknologi-2026-untuk-startup-di-3-provinsi", kind: non-english, country: ID}
  - {url: "https://ukmindonesia.id/baca-deskripsi-program/beasiswa-inkubasi-rocket-2026-gelombang-2-dibuka-bidik-youthpreneur-1730-tahun", kind: non-english, country: ID}

  # Vietnam
  - {url: "https://nic.gov.vn/", kind: non-english, country: VN}
  - {url: "https://doanhnghiephoinhap.vn/phat-dong-cuoc-thi-tim-kiem-tai-nang-khoi-nghiep-sang-tao-nghe-an-mo-rong-2026-136789.html", kind: non-english, country: VN}

  # Philippines
  - {url: "https://www.qboinnovation.com/programs-spotlight", kind: portal, country: PH}
  - {url: "https://www.qboinnovation.com/startup-pinay", kind: program, country: PH}
  - {url: "https://www.pchrd.dost.gov.ph/sgp/", kind: program, country: PH}
  - {url: "https://www.pcaarrd.dost.gov.ph/index.php/quick-information-dispatch-qid-articles/dost-pcaarrd-opens-call-for-2026-startup-grant-fund-program", kind: program, country: PH}

  # Cambodia
  - {url: "https://tsc.gov.kh/", kind: portal, country: KH}

  # Brunei
  - {url: "https://www.bedb.gov.bn/icentre", kind: program, country: BN}
  - {url: "https://www.business.gov.bn/registration-for-dares-accelerate-now-open/", kind: program, country: BN}
  - {url: "https://www.business.gov.bn/dare-inviting-brunei-smes-to-apply-for-grants-up-to-20k/", kind: program, country: BN}

  # Regional / single programs
  - {url: "https://startup.google.com/programs/accelerator/southeast-asia/", kind: program, country: ASEAN}
  - {url: "https://www.antler.co/pitch", kind: regional, country: ASEAN}
  - {url: "https://ventures.adb.org/", kind: program, country: ASEAN}
  - {url: "https://www.youthcolab.org/", kind: regional, country: ASEAN}
  - {url: "https://fi.co/join", kind: regional, country: ASEAN}
  - {url: "https://aws.amazon.com/startups/credits", kind: program, country: GLOBAL}

  # Aggregators
  # e27 answers our crawler with HTTP 403. Respect that: don't fake a browser user agent.
  # nia.or.th, sginnovate.com and iterative.vc disallow us in robots.txt.
  - {url: "https://devpost.com/hackathons?challenge_type[]=in-person&search=asia", kind: aggregator, country: ASEAN}
```

## Reserved for the live paste-a-URL moment. Don't seed these.

| | URL | Why |
|---|---|---|
| **Primary** | `https://ukmindonesia.id/baca-deskripsi-program/brin-rise-2026-dibuka-untuk-20-startup-track-baru-berpeluang-dapat-pendanaan-rp300-juta` | Bahasa Indonesia; BRIN RISE 2026, open until 13 Nov 2026, up to Rp300 juta. A live, clear and relevant result. |
| Backup | `https://ukmindonesia.id/baca-deskripsi-program/ui-incubate-2026-resmi-dibuka-kesempatan-startup-kembangkan-inovasi-bersama-ekosistem-ui` | Bahasa Indonesia; UI Incubate 2026, funding up to Rp600–800 juta. |

Test the primary URL once with `python -m gateway ingest <url>` before the demo, then delete that record so the demo shows a fresh result.

## Coverage notes for the gap map and the pitch

- No seeds for **Laos** or **Myanmar**, and Cambodia has only one. That's an honest gap to show: "coverage so far".
- Several 2026 calls are already closed (PCAARRD SGF, Google SEA, Global Startup Hub). Good for testing deadline and status handling; the "open now" count will be lower than the total.
- Startup SG grant amounts differ across third-party guides; trust only the extraction from the official page.
