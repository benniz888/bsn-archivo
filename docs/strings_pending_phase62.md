# Strings for PHASE_62_CUADRICULA_FIX: APPROVED by the owner, live in `web/js/games.js`

New or changed public Spanish strings. Proposed text only; not final until approved. Until then the UI
shows the draft behind a visible `[PENDIENTE ...]` prefix (in `web/js/games.js`, `submitGuess`) so nobody
mistakes it for approved copy. Approval = remove the prefix and swap in the final wording.

| Id | Where | Shown now (placeholder) | Proposed final text | When |
|---|---|---|---|---|
| P62-R1 | Wrong guess, player fails a criterion | `[PENDIENTE P62-R] {nombre}: el archivo no lo registra en «{criterio}» ni «{criterio}». Intento gastado.` | `{nombre} no figura en el archivo como «{criterio}». Intento gastado.` (second criterion joined with `ni`, only the ones that failed) | Replaces `{nombre} no cumple {fila} + {columna}. Intento gastado.`, which blamed both criteria even when one was met. |
| P62-R2 | Wrong guess, archive has no data on a criterion | same prefix, `...; sin datos en el archivo para «{criterio}»` | `El archivo no tiene datos de {nombre} para «{criterio}», así que no se puede confirmar. Intento gastado.` | Player has no club list (club axes), no position (Base o escolta / Poste) or no scoring figure (20+ puntos). Honest: absence of data is not "did not play there". |
| P62-A | Typed text fits more than one player | `[PENDIENTE P62-A] Hay {n} jugadores que encajan con eso. Escribe más del nombre. No gasta intento.` | `Hay {n} jugadores que encajan con eso. Escribe más del nombre.` | Before: the first match in the pool was silently chosen and judged. |

Open question for the owner on P62-R2: the attempt is still spent when data is missing (current game rule, unchanged). Say if a missing-data rejection should be free instead.

Unchanged: `Ese nombre no está en la nómina verificada. No gasta intento.` and `Ya lo usaste. No gasta intento.`

## Approved (owner, 2026-10-10)
Placeholders removed. Live text:
- P62-R1: `{nombre} no figura en el archivo como «{criterio}» ni «{criterio}». Intento gastado.`
- P62-R2: `El archivo no tiene datos de {nombre} para «{criterio}», así que no se puede confirmar. No gasta intento.` Owner decision: a rejection resting only on missing archive data does not cost an attempt (if one criterion truly failed, the attempt is spent and R1 names only that one).
- P62-A: `Hay {n} jugadores que encajan con eso. Escribe más del nombre. No gasta intento.`
