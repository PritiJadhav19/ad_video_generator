def generate_ad_json(meta: dict) -> dict:
    brand = meta.get("brand", "Brand")
    product = meta.get("product", "Product")
    benefits = meta.get("benefits", [])
    offer = meta.get("offer")
    cta = meta.get("cta", "Order Now")
    duration = int(meta.get("duration_sec", 15))
    tone = (meta.get("tone") or "Relatable, punchy").lower()
    language = (meta.get("language") or "Hinglish").lower()

    # Benefits safe picks
    b1 = benefits[0] if len(benefits) > 0 else "Visible results"
    b2 = benefits[1] if len(benefits) > 1 else "Lightweight & easy"
    b3 = benefits[2] if len(benefits) > 2 else "Worth every rupee"

    # Simple language helpers
    def L(hinglish: str, hindi: str, english: str) -> str:
        if "hindi" in language and "hinglish" not in language:
            return hindi
        if "english" in language:
            return english
        return hinglish  # default Hinglish

    # More powerful hooks (3 options)
    hooks = [
        {
            "id": "hook_a",
            "line": L(
                f"Stop scrolling! {product} ka glow/upgrade hack dekh lo 😳",
                f"रुको! {product} का असली असर अभी देखो 😳",
                f"Stop scrolling—watch what {product} can really do 😳"
            ),
            "visual": "Fast cut + bold text pop",
            "visual_query": f"{product} closeup aesthetic vertical",
            "text_style": "BIG_BOLD",
            "animation": "pop_in",
            "sfx": "whoosh"
        },
        {
            "id": "hook_b",
            "line": L(
                f"Har roz same problem? Bas {product}… aur game over.",
                f"हर दिन वही परेशानी? बस {product}… और खत्म!",
                f"Same problem every day? Just {product}—game over."
            ),
            "visual": "Problem-to-solution transition",
            "visual_query": f"person frustrated then happy using {product} vertical",
            "text_style": "GLITCH",
            "animation": "swipe_cut",
            "sfx": "click"
        },
        {
            "id": "hook_c",
            "line": L(
                f"{brand} ne drop kiya hai something CRAZY… miss mat karna 👀",
                f"{brand} ने कुछ CRAZY लॉन्च किया है… मिस मत करना 👀",
                f"{brand} just dropped something CRAZY… don’t miss this 👀"
            ),
            "visual": "Reveal + zoom-in product hero",
            "visual_query": f"{product} product reveal studio lighting vertical",
            "text_style": "NEON",
            "animation": "zoom_in",
            "sfx": "boom"
        },
    ]

    # Pick a default hook based on duration/tone
    chosen_hook = hooks[0]
    if duration > 15:
        chosen_hook = hooks[1] if "funny" in tone or "genz" in tone else hooks[2]

    # Helper: scene builder
    def scene(t0, t1, vo, on_screen, shot, camera, query, anim, sfx, overlay=None):
        return {
            "t_start": t0,
            "t_end": t1,
            "vo": vo,
            "on_screen_text": on_screen,
            "shot": shot,                 # storyboard shot description
            "camera": camera,             # camera movement idea
            "visual_query": query,         # for stock video search
            "text_animation": anim,        # for kinetic text later
            "sfx": sfx,                    # sound effect cue
            "overlay": overlay or []       # optional stickers/icons/buttons
        }

    # CTA line (stronger)
    cta_line = L(
        f"{offer + ' — ' if offer else ''}{cta}! Abhi try karo 🔥",
        f"{offer + ' — ' if offer else ''}{cta}! अभी ट्राय करो 🔥",
        f"{offer + ' — ' if offer else ''}{cta}! Try it now 🔥"
    )

    # Build scenes with more “ad-like” pacing
    if duration <= 15:
        scenes = [
            scene(
                0, 2.5,
                chosen_hook["line"],
                [brand, product, L("STOP SCROLLING", "रुको!", "STOP SCROLLING")],
                shot="Quick montage: problem face → product flash → reaction",
                camera="Handheld + quick zoom cuts",
                query=chosen_hook["visual_query"],
                anim="pop_in",
                sfx=chosen_hook["sfx"],
                overlay=["🔥", "👀"]
            ),
            scene(
                2.5, 6.0,
                L(f"1 second mein samjho: {b1}.", f"1 सेकंड में समझो: {b1}.", f"In 1 second: {b1}."),
                [L("RESULT:", "नतीजा:", "RESULT:"), b1],
                shot="Close-up of applying product / texture shot",
                camera="Macro close-up + slow push-in",
                query=f"{product} texture closeup vertical",
                anim="slide_up",
                sfx="soft_pop",
                overlay=["✅"]
            ),
            scene(
                6.0, 9.5,
                L(f"Plus, {b2}.", f"और साथ में, {b2}.", f"Plus, {b2}."),
                [b2, L("NO HEAVY FEEL", "भारी नहीं", "NO HEAVY FEEL")],
                shot="Mirror shot / smooth application / glow angle",
                camera="Smooth pan left-to-right",
                query=f"skincare mirror glow vertical",
                anim="type_on",
                sfx="tap",
                overlay=["✨"]
            ),
            scene(
                9.5, 13.0,
                L(f"Best part? {b3}.", f"सबसे बढ़िया? {b3}.", f"Best part? {b3}."),
                [b3, L("TRUSTED", "भरोसेमंद", "TRUSTED")],
                shot="Social proof / reviews style moment",
                camera="Swipe between review cards",
                query="happy customer review phone screen vertical",
                anim="swipe_cut",
                sfx="swipe",
                overlay=["⭐ 4.8", "💬"]
            ),
            scene(
                13.0, 15.0,
                cta_line,
                [L("LIMITED TIME", "सीमित समय", "LIMITED TIME"), cta],
                shot="Product hero shot + CTA button",
                camera="Zoom-in + light flare",
                query=f"{product} product hero shot vertical",
                anim="cta_bounce",
                sfx="boom",
                overlay=["🛒", "👇"]
            ),
        ]
    else:
        scenes = [
            scene(
                0, 4.0,
                chosen_hook["line"],
                [brand, product],
                shot="Story hook: problem moment → product appears",
                camera="Fast cuts + punch zoom",
                query=chosen_hook["visual_query"],
                anim="pop_in",
                sfx=chosen_hook["sfx"],
                overlay=["👀"]
            ),
            scene(
                4.0, 10.0,
                L(f"First: {b1}. Real talk.", f"पहला: {b1}. सच में.", f"First: {b1}. Real talk."),
                [L("BENEFIT #1", "फायदा #1", "BENEFIT #1"), b1],
                shot="Close-up + application + result angle",
                camera="Slow push-in + cut on beat",
                query=f"{product} skincare application vertical",
                anim="slide_up",
                sfx="soft_pop",
                overlay=["✅"]
            ),
            scene(
                10.0, 18.0,
                L(f"Second: {b2}. Daily use friendly.", f"दूसरा: {b2}. रोज़ के लिए सही.", f"Second: {b2}. Daily-friendly."),
                [L("BENEFIT #2", "फायदा #2", "BENEFIT #2"), b2],
                shot="Lifestyle b-roll: morning routine",
                camera="Pan + match cut",
                query="morning skincare routine aesthetic vertical",
                anim="type_on",
                sfx="tap",
                overlay=["✨"]
            ),
            scene(
                18.0, 24.0,
                L(f"Third: {b3}. Value for money.", f"तीसरा: {b3}. पैसे वसूल.", f"Third: {b3}. Value for money."),
                [L("BENEFIT #3", "फायदा #3", "BENEFIT #3"), b3],
                shot="Before/after style split-screen idea",
                camera="Split-screen wipe",
                query="before after skincare glow vertical",
                anim="split_wipe",
                sfx="swipe",
                overlay=["⭐", "💬"]
            ),
            scene(
                24.0, 30.0,
                cta_line,
                [L("SALE", "ऑफर", "SALE"), offer or "", cta],
                shot="Product hero + offer card + CTA",
                camera="Zoom + shake on beat",
                query=f"{product} sale promo vertical",
                anim="cta_bounce",
                sfx="boom",
                overlay=["🛒", "👇"]
            ),
        ]

    return {
        "duration": duration,
        "hooks": hooks,        # you can show these in UI later to choose
        "chosen_hook": chosen_hook["id"],
        "scenes": scenes
    }