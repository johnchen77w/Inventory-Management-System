"use client";

import { WsAlert } from "./useWebSocket";

type Props = {
  alerts: WsAlert[];
  onDismiss: (id: number) => void;
};

function getAlertStyle(type: string) {
  switch (type) {
    case "item_restocked":
      return { bgColor: "#16a34a", title: "Item Restocked" };
    case "item_withdrawn":
      return { bgColor: "#ca8a04", title: "Item Withdrawn" };
    case "low_stock_alert":
    default:
      return { bgColor: "#dc2626", title: "Low Stock Alert" };
  }
}

export default function AlertToast({ alerts, onDismiss }: Props) {
  if (alerts.length === 0) return null;

  return (
    <div className="fixed top-4 right-4 z-50 flex flex-col gap-3 max-w-sm">
      {alerts.map((alert) => {
        const style = getAlertStyle(alert.type);
        return (
          <div
            key={alert.id}
            style={{ backgroundColor: style.bgColor }}
            className="text-white rounded-xl shadow-lg p-4 animate-slide-in"
          >
            <div className="flex justify-between items-start gap-3">
              <div>
                <p className="font-bold text-sm">{style.title}</p>
                <p className="text-sm mt-1">
                  <span className="font-semibold">{alert.name}</span>
                  {alert.sku && <span className="opacity-80"> ({alert.sku})</span>}
                </p>
                {alert.type === "low_stock_alert" ? (
                  <p className="text-sm mt-1 opacity-90">
                    Quantity: <span className="font-bold">{alert.quantity}</span>
                    {" / Threshold: "}{alert.threshold}
                  </p>
                ) : (
                  <p className="text-sm mt-1 opacity-90">
                    {alert.quantity_before} → <span className="font-bold">{alert.quantity_after}</span>
                  </p>
                )}
                {alert.notes && (
                  <p className="text-xs mt-1 opacity-75">{alert.notes}</p>
                )}
                {alert.location && (
                  <p className="text-xs mt-1 opacity-75">{alert.location}</p>
                )}
              </div>
              <button
                onClick={() => onDismiss(alert.id)}
                className="text-white opacity-70 hover:opacity-100 text-lg leading-none"
              >
                &times;
              </button>
            </div>
          </div>
        );
      })}
    </div>
  );
}
