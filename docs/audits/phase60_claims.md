# PHASE_60 audit: claims (testimonials, ratings, superlatives, "oficial", "verificado", 100%)

Method: case-insensitive grep over web/index.html and web/js/*.js (tabs.js POOL_* data lines excluded) for: testimon|estrellas|rating|garantiz|oficial|verificad|100 ?%|único/a|mejor|completo|récord|máximo. Counts: tabs.js verificad 7, oficial 11, completo 20, mejor 10, único 7, récord 59; index.html oficial 9, récord 23. **Testimonials: 0. Star ratings: 0. "100%" as a claim: 0** (the one `100%` hit, tabs.js L2931, is an SVG `width:100%` style).

Most superlatives ("Máximo anotador histórico", "récord") are archive data statements, not marketing; they stay but need sourcing in the data, not rewording. Rows below are the ones that read as claims about the SITE or imply league endorsement. Proposed text is a proposal only; all public strings need your approval.

| file:line | current | issue | proposed neutral wording |
|---|---|---|---|
| index.html:396 / tabs.js:5963 | "Todos usan la misma nómina verificada de jugadores, así que ninguno inventa una respuesta." | "verificada" + absolute claim; Cuadrícula currently rejects valid answers (see summary section 7) | "Todos usan la misma nómina de jugadores del archivo." |
| games.js:250, 353 | "La nómina verificada es de N jugadores" / "no está en la nómina verificada" | "verificada" | "la nómina del archivo" |
| tabs.js:5773 | "Cuánto del archivo está verificado, por década" | "verificado" implies authority | "Cuánto del archivo está cubierto, por década, y de dónde sale cada dato." |
| index.html:463 | "cuánto del archivo está verificado" | same | "cuánto del archivo está cubierto" |
| tabs.js:3179 | "Wikipedia. Todos verificados contra los CSV del proyecto." | "verificados" | "Wikipedia, contrastado con los CSV del proyecto." |
| tabs.js:3747 | "solo hay biografía verificada de N" | same | "solo hay biografía documentada de N" |
| tabs.js:2071 | tag "Colores verificados" / "Colores aproximados" | "verificados" | "Colores de Wikipedia" / "Colores aproximados" |
| tabs.js:1429, 1457, 1486, 1492, 1693 | "app oficial del BSN", "Titulares vistos en la app oficial" | "oficial" is the league's own name for its app; accurate, but pairs with a non-official site | keep, but name it: "la app del BSN" |
| tabs.js:3177, 3099 | "el export oficial del BSN" | accurate source note | keep as a source citation |
| index.html:225 | "Canales oficiales" | accurate (league channels) | keep, or "Canales del BSN" |
| tabs.js:3186 | "Con cero imágenes, todo se ve igual de bien." | self-praise | "Por eso el archivo no usa imágenes." |
| tabs.js:3186 | "es la razón principal por la que Apple rechaza apps de este tipo" | unsourced claim about Apple | remove the clause |
| index.html:583,651,732 | "récord mundial extraoficial" (Jonathan García, 33 asistencias) | claim needs a source in the string | add source or "según la prensa" |
| tabs.js:346 | "el que todavía se lo debe a su fanaticada" | editorial voice about a club | owner decision (club lore, phase 66) |
| tabs.js:373 | "el único pueblo de Puerto Rico fundado por negros libres" | strong factual claim, unsourced here | needs a source or removal (phase 66) |
| tabs.js:3484 | "nombrado el Mejor Jugador del Mundo" | factual claim | needs source line (phase 66) |
| tabs.js:2179 | "No hay un registro oficial de titulares ... una inferencia declarada, no un dato verificado" | correct, honest wording | keep |
| index.html:7,12,16 | "no oficial" in meta description | good | keep |
