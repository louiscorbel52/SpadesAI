import numpy as np
import deck52

from collections import namedtuple
from util import follow_suit, eval_position

class Searcher:

    def __init__(self, playmodel, evalmodel, decl_i, strain_i):
        self.playmodel = playmodel
        self.evalmodel = evalmodel
        self.decl_i = decl_i
        self.strain_i = strain_i

    def search(self, samples, candidates, on_play_i, current_trick, n_decl_tricks, depth, search_for):
        n_samples = samples.shape[0]

        # create a stack for each sample and put the initial operation on the stack
        stacks = [
            [
                ForeachCandidateStart(
                    on_play_i=on_play_i,
                    current_trick=current_trick,
                    n_decl_tricks=n_decl_tricks,
                    depth=depth,
                    candidates=candidates,
                    results={}
                )
            ] 
            for sample in samples
        ]

        # this will have the result for each sample in the end
        results = [None] * n_samples

        while any(len(stack) > 0 for stack in stacks):
            for sample_i, stack in enumerate(stacks):
                # execute until we reach a point where we need to call a model (play-card or eval-pos)
                while True:
                    if not stack:
                        break

                    op = stack.pop()

                    if isinstance(op, GetCandidates):
                        stack.append(op)
                        break

                    elif isinstance(op, EvalPosition):
                        stack.append(op)
                        break

                    elif isinstance(op, NewTrick):
                        n_tricks_left = np.sum(samples[sample_i, op.on_play_i])
                        if n_tricks_left == 0:
                            results[sample_i] = {None: op.n_decl_tricks}
                        elif op.depth == 0 and n_tricks_left >= 2:
                            stack.append(EvalPosition(op.on_play_i, op.n_decl_tricks, op.depth))
                        else:
                            stack.append(GetCandidates(op.on_play_i, [], op.n_decl_tricks, op.depth))

                    elif isinstance(op, RecSearch):
                        if len(op.current_trick) == 4:
                            stack.append(TrickComplete(op.on_play_i, op.current_trick, op.n_decl_tricks, op.depth))
                        else:
                            stack.append(GetCandidates(op.on_play_i, op.current_trick, op.n_decl_tricks, op.depth))

                    elif isinstance(op, ForeachCandidateEnd):
                        samples[sample_i, op.on_play_i, op.candidates[0]] = 1 # unplay the card
                        is_maximizer = (self.decl_i % 2) == (op.on_play_i % 2)
                        _, score = sorted(results[sample_i].items(), key=lambda x: x[1], reverse=not is_maximizer)[0]
                        cand_res = {op.candidates[0]: score, **op.results}
                        stack.append(
                            ForeachCandidateStart(
                                on_play_i=op.on_play_i,
                                current_trick=op.current_trick,
                                n_decl_tricks=op.n_decl_tricks,
                                depth=op.depth,
                                candidates=op.candidates[1:],
                                results=cand_res
                            )
                        )

                    elif isinstance(op, ForeachCandidateStart):
                        if len(op.candidates) == 0:
                            results[sample_i] = op.results
                        else:
                            samples[sample_i, op.on_play_i, op.candidates[0]] = 0 # play the card
                            # push on the stack for later (we'll do this after recursive call with first candidate)
                            stack.append(ForeachCandidateEnd(op.on_play_i, op.current_trick, op.n_decl_tricks, op.depth, op.candidates, op.results))
                            # push recursive call on the stack
                            stack.append(RecSearch(
                                on_play_i=(op.on_play_i + 1) % 4,
                                current_trick=[*op.current_trick, op.candidates[0]],
                                n_decl_tricks=op.n_decl_tricks,
                                depth=op.depth
                            ))
                        
                    elif isinstance(op, TrickComplete):
                        trick_winner_i = (op.on_play_i + deck52.get_trick_winner_i(op.current_trick, (self.strain_i - 1) % 5)) % 4
                        is_decl_win = (trick_winner_i % 2) == (self.decl_i % 2)
                        stack.append(NewTrick(on_play_i=trick_winner_i, n_decl_tricks=op.n_decl_tricks + is_decl_win, depth=op.depth - 1))

            # now we can't progress further on any of the stacks
            # we call the models and put the next operation on the stacks

            samples_to_play = []
            samples_to_eval = []
            for sample_i, stack in enumerate(stacks):
                if not stack:
                    continue
                if isinstance(stack[-1], GetCandidates):
                    samples_to_play.append(sample_i)
                elif isinstance(stack[-1], EvalPosition):
                    samples_to_eval.append(sample_i)
                else:
                    raise Exception(f'unexpecyted operation on top of stack: {stack[-1]}')
                
            # run the play model for all samples_to_play
            if samples_to_play:
                X = np.zeros((len(samples_to_play), 369))
                X[:, 364 + self.strain_i] = 1
                trick_suit = np.zeros((len(samples_to_play), 4), dtype=np.uint8)
                whos_turn = []
                for i, sample_i in enumerate(samples_to_play):
                    op = stacks[sample_i][-1]
                    whos_turn.append(op.on_play_i)
                    n_trick_cards = len(op.current_trick)
                    if n_trick_cards > 0:
                        trick_suit[i, op.current_trick[0] // 13] = 1
                    if n_trick_cards > 0:
                        X[i, 312 + op.current_trick[n_trick_cards - 1]] = 1
                    if n_trick_cards > 1:
                        X[i, 260 + op.current_trick[n_trick_cards - 2]] = 1
                    if n_trick_cards > 2:
                        X[i, 208 + op.current_trick[n_trick_cards - 3]] = 1

                    X[i, :52] = samples[sample_i, op.on_play_i, :]
                    X[i, 52:104] = samples[sample_i, (op.on_play_i + 1) % 4, :]
                    X[i, 104:156] = samples[sample_i, (op.on_play_i + 2) % 4, :]
                    X[i, 156:208] = samples[sample_i, (op.on_play_i + 3) % 4, :]
                
                p_peek = self.playmodel.model(X)
                p_follow = follow_suit(p_peek, X[:,:52], trick_suit)

                for i in range(len(samples_to_play)):
                    candidates = [(p_follow[i, c], c) for c in np.nonzero(p_follow[i])[0] if p_follow[i, c] >= 0.05]  
                    if not candidates:
                        candidates = [(p_follow[i, c], c) for c in np.nonzero(p_follow[i])[0]]
                    candidates = sorted(candidates, reverse=True)

                    op = stacks[samples_to_play[i]].pop()

                    if candidates[0][0] >= 0.9 or whos_turn[i] not in search_for or op.depth < depth - 3 or (op.depth < depth and op.current_trick):
                        candidates = [candidates[0][1]]
                    else:
                        candidates = [c for _, c in candidates]
                    
                    stacks[samples_to_play[i]].append(
                        ForeachCandidateStart(
                            on_play_i=op.on_play_i,
                            current_trick=op.current_trick,
                            n_decl_tricks=op.n_decl_tricks,
                            depth=op.depth,
                            candidates=candidates,
                            results={}
                        )
                    )

            # run the eval model for all samples_to_eval
            if samples_to_eval:
                for sample_i in samples_to_eval:
                    op = stacks[sample_i].pop()
                    p_tricks = eval_position(self.evalmodel, samples[sample_i:sample_i+1], op.on_play_i, self.decl_i, self.strain_i)
                    tricks_ev = op.n_decl_tricks + p_tricks[0] @ np.arange(14)
                    results[sample_i] = {None: tricks_ev}

        return results


ForeachCandidateStart = namedtuple('ForeachCandidateStart', ['on_play_i', 'current_trick', 'n_decl_tricks', 'depth', 'candidates', 'results'])
ForeachCandidateEnd = namedtuple('ForeachCandidateEnd', ['on_play_i', 'current_trick', 'n_decl_tricks', 'depth', 'candidates', 'results'])

TrickComplete = namedtuple('TrickComplete', ['on_play_i', 'current_trick', 'n_decl_tricks', 'depth'])

NewTrick = namedtuple('NewTrick', ['on_play_i', 'n_decl_tricks', 'depth'])

GetCandidates = namedtuple('GetCandidates', ['on_play_i', 'current_trick', 'n_decl_tricks', 'depth'])

EvalPosition = namedtuple('EvalPosition', ['on_play_i', 'n_decl_tricks', 'depth'])

RecSearch = namedtuple('RecSearch', ['on_play_i', 'current_trick', 'n_decl_tricks', 'depth'])

