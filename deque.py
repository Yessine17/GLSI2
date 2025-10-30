# تحويل AFN (NFA) → AFD (DFA) بالـpowerset construction
 

from collections import deque

def epsilon_closure(states, nfa, eps_symbol='ε'):
    """احسب ε-closure لمجموعة حالات (set)"""
    stack = list(states)
    closure = set(states)
    while stack:
        s = stack.pop()
        for t in nfa.get(s, {}).get(eps_symbol, []):
            if t not in closure:
                closure.add(t)
                stack.append(t)
    return closure

def move(states, symbol, nfa):
    """المجموعة التي نصلها من 'states' بقراءة 'symbol' (بدون ε)"""
    result = set()
    for s in states:
        for t in nfa.get(s, {}).get(symbol, []):
            result.add(t)
    return result

def nfa_to_dfa(nfa, start_state, accept_states, alphabet, eps_symbol='ε'):
    """
    nfa: dict: state -> {symbol -> [states], ...}
    start_state: q0 of NFA
    accept_states: set/list of NFA accept states
    alphabet: list of input symbols (لا تضع 'ε' هنا)
    """
    # بداية: إغلاق ε على الحالة الابتدائية
    start_closure = frozenset(epsilon_closure({start_state}, nfa, eps_symbol))
    state_map = {start_closure: 0}   # تخطيط مجموعة -> رقم حالة DFA
    rev_map = [start_closure]        # لعرض المجموعات بالترتيب
    dfa_transitions = {}             # رقم حالة -> {symbol: رقم حالة}
    dfa_accepts = set()
    queue = deque([start_closure])

    while queue:
        current = queue.popleft()
        cur_id = state_map[current]
        dfa_transitions[cur_id] = {}
        # هل هذه حالة قبول؟
        if any(s in accept_states for s in current):
            dfa_accepts.add(cur_id)

        for sym in alphabet:
            # نتحرك ثم نطبق ε-closure
            moved = move(current, sym, nfa)
            if not moved:
                # يمكنك تجاهل الانتقالات الغير معرفة أو تمثيلها كحالة ميتة
                continue
            closure = frozenset(epsilon_closure(moved, nfa, eps_symbol))
            if closure not in state_map:
                state_map[closure] = len(rev_map)
                rev_map.append(closure)
                queue.append(closure)
            dfa_transitions[cur_id][sym] = state_map[closure]

    # نتائج مرتبة
    dfa = {
        'start': state_map[start_closure],
        'accepts': dfa_accepts,
        'transitions': dfa_transitions,
        'state_sets': rev_map  # للاطلاع: أي رقم يمثل أي مجموعة من حالات NFA
    }
    return dfa

# ---------- مثال عملي ----------
if __name__ == "__main__":
    # مثال AFN:
    # حالات: 0,1,2,3
    # انتقالات: من 0 عن ε إلى 1 و2، من 1 عن 'a' إلى 1 و2، من 2 عن 'b' إلى 3، الخ.
    nfa = {
        0: {'ε': [1,2]},
        1: {'a': [1,2]},
        2: {'b': [3]},
        3: {}  # حالة نهائية مثلاً
    }
    start = 0
    accepts = {3}
    alphabet = ['a','b']  # لا تضع 'ε' هنا

    dfa = nfa_to_dfa(nfa, start, accepts, alphabet, eps_symbol='ε')

    # طباعة النتيجة بطريقة مفهومة (الحالات الرقمية {0,1,2,...} مرتبطة بمجموعات NFA)
    print("تخطيط حالات DFA (رقم => مجموعة حالات NFA):")
    for i, sset in enumerate(dfa['state_sets']):
        print(f"  {i} => {set(sset)}")
    print("\nحالة البداية في DFA:", dfa['start'])
    print("حالات القبول في DFA:", dfa['accepts'])
    print("\nانتقالات DFA (رقم الحالة -> {symbol: رقم الحالة}):")
    for st, trans in dfa['transitions'].items():
        print(f"  {st} : {trans}")
