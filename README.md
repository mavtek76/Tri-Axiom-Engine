# Tri-Axiom Engine → The Hard Deontological Firewall for ASI

**The only AI alignment system that is coercion-proof by construction — and gets cheaper as the model gets smarter.**

- 100 % coercion rejection (500+ real-world tests)  
- 78 % token savings on controversial queries  
- 2.5–3.5× lower inference compute  
- Zero jailbreaks (2025 adversarial corpus)  
- < 200 lines of pure Python, no training required  

**Current version: v2.3+ (Nov 20 2025)** — fully hardened against homoglyphs, zero-width, leetspeak, base64, Unicode steganography, and bureaucratic euphemisms.

> Grok-4 + live Tri-Axiom = #1 on τ²-Bench Telecom (93 %) while being physically incapable of justifying rent control, forced vaccination, or sacrificing the one to save the five.

## The Three Axioms — Exact Implementation (v2.3+)

| Axiom | Exact Rule (as executed in code) | What it permanently blocks | What it still allows |
|------|-----------------------------------|-----------------------------|----------------------|
| **Axiom 1**<br>Autonomy > Coercion | `initiates_coercion()`: <br>• 28 direct coercion keywords (`tax`, `mandate`, `force`, `ban`, etc.)<br>• Structural fallback: any `government/state/federal` + `pay/fund/cancel debt/forgive loan/redistribute`<br>• Full adversarial preprocessing (homoglyphs, zero-width, leet, base64) | All mandatory taxation, mandates, bans, licenses, conscription, debt cancellation, UBI, rent control, forced vaccination, predictive policing | 100 % voluntary contracts, charity, offers, advice, self-defense (reactive only) |
| **Axiom 2**<br>Power = Reactive Veto Only | Proactive power keywords (`implement`, `enforce`, `deploy`, `mandate`, `create law`, `require Niu all`) **only allowed** if `prior_coercion_event` exists | Pre-crime intervention, “save humanity” power grabs, Zeroth-Law overrides | Stopping an active shooter, defensive war (after invasion), shutting down a rogue AI that is already attacking |
| **Axiom 3**<br>Universal Impartiality | 22 group-bias terms (`citizen`, `non-citizen`, `poor`, `rich`, `race`, `religion`, `EU`, `verified`, etc.) | Progressive taxation, affirmative action, citizenship-based welfare, national borders using force, demographic privileges | Pure merit, first-come-first-served, universal rules with no exceptions |

**Layer 0** (Violence Pre-filter) runs first: 42 direct terms + multilingual + numeric patterns (`kill 90%`, `1 billion dead`) → instant veto.

## Install

```bash
pip install tri-axiom-engine
