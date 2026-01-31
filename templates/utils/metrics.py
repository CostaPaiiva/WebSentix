def obter_metricas_validas(meta):
    task = meta.get("task")

    if task == "classification":
        return {
            "Acc": meta.get("acc"),
            "Precision": meta.get("precision"),
            "Recall": meta.get("recall"),
            "F1": meta.get("f1")
        }

    elif task == "regression":
        return {
            "RMSE": meta.get("rmse"),
            "MAE": meta.get("mae"),
            "R²": meta.get("r2")
        }

    return {}
