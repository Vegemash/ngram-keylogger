# Advanced config showing some of the features ngram-keylogger offers

import ngram_keylogger


REST_DURATION = 1  # seconds. Waiting longer than that breaks up n-grams.
PROMPTERS = ['i3lock', 'swaylock', 'pinentry']
PROMPTERS_RESCAN = 5

CUSTOM_REPLACEMENT_TABLE = {
    'j-j': 'vdown',  # going down two times in vim
    'j-j-j': 'vdown',  # going down three times in vim
    'k-k': 'vup',  # going up two times in vim
    'k-k-k': 'vup',  # going up three times in vim
    'leftalt-a': 'vim-move-split-left', 
}


def context_name(t):
    if not isinstance(t, str):
        return 'other'

    if re.match(r'^\[\d+\]@$' + HOSTNAME, t):  # gpg password prompt
        return ngram_keylogger.CONTEXT_IGNORE
    if re.match(r'kinit$' + HOSTNAME, t):
        return ngram_keylogger.CONTEXT_IGNORE

    if re.match('.*Mozilla Firefox$', t):
        return 'browser'

    m = re.match(r'.* > vi > \[(\w+)\].* > .* \[(INS|RPL|VIL|VIB)\]$', t)
    if m:
        return f'term:vi:{m.group(1)}:{m.group(2).lower()}'
    m = re.match(r'.* > vi > \[(\w+)\].* > .*', t)
    if m:
        return f'term:vi:{m.group(1)}:nrm'
    if re.match(r'.* > vi.*', t):
        return 'term:vi'

    m = re.match(r'.* > \d+ > (\w+)', t)
    if m:
        if m.group(1) in ('nmtui', 'nmtui-connect'):
            return ngram_keylogger.CONTEXT_IGNORE
        return f'term:{m.group(1)}'
    if re.match(r'.* > *', t):
        return 'term:other'
    return 'other'
def detect_prompters(p):
    for s in PROMPTERS:
        if s in p.name():
            return p.name()


async def action_generator_(event_and_extras_gen):
    """
    Converts evdev events to sequences of actions like
    'a', 'Y', '.', '&', 'control-shift-c', 'Left+' or 'close window'.
    """
    gen = event_and_extras_gen
    gen = ngram_keylogger.aspect.keys_only(gen)
    gen = ngram_keylogger.aspect.inactivity(gen, timeout=REST_DURATION)
    gen = ngram_keylogger.aspect.modifiers(gen)
    gen = ngram_keylogger.aspect.repeating(gen)

    # current_window_titles = ngram_keylogger.util.i3ipc.current_window_titles()
    async for event, extras in gen:
        if extras['after_inactivity']:
            yield ngram_keylogger.NOTHING, None
        repeat = extras['repeat']
        active_modifiers_prefix = extras['active_modifiers_prefix']

        short = ngram_keylogger.util.short_key_name(event.code)
        short = active_modifiers_prefix + short
        # window_title = await current_window_titles.__anext__()
        # context = context_name(window_title)
        yield short + ('+' if repeat else ''), None


action_generator = ngram_keylogger.filter.apply_filters(action_generator_, [
    ngram_keylogger.filter.shift_printables,
    ngram_keylogger.filter.abbreviate_controls,
    ngram_keylogger.filter.make_replace(CUSTOM_REPLACEMENT_TABLE),
    ngram_keylogger.filter.make_process_scan(detect_prompters,
                                             PROMPTERS_RESCAN),
])
