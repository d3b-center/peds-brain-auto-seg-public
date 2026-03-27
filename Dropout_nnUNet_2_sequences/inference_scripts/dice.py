def diceFunction(pred, ground):
    if pred.shape != ground.shape:
        raise ValueError("Shape mismatch: pred and ground must have the same shape.")

    intersection = np.logical_and(pred, ground)
    if ((pred.sum() == 0) and (ground.sum() == 0)):
        return 1.0
    return (2.0 * intersection.sum()) / (pred.sum() + ground.sum())

def computeDiceScores(pred, ground):
    return (
        diceFunction(pred > 0, ground > 0),                              # wt
        diceFunction(pred == 1, ground == 1),                            # et
        diceFunction(pred == 2, ground == 2),                            # net
        diceFunction(pred == 3, ground == 3),                            # cyst
        diceFunction(pred == 4, ground == 4),                            # edema
    )
