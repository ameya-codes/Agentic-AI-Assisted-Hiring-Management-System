import * as React from "react";
import { readStoredRequisitionId, writeStoredRequisitionId } from "../requisitionStorage";

type Ctx = {
  activeJobId: number | null;
  setActiveJobId: (id: number | null) => void;
};

const RequisitionContext = React.createContext<Ctx | null>(null);

export function RequisitionProvider({ children }: { children: React.ReactNode }) {
  const [activeJobId, setActiveJobIdState] = React.useState<number | null>(() => readStoredRequisitionId());

  const setActiveJobId = React.useCallback((id: number | null) => {
    setActiveJobIdState(id);
    writeStoredRequisitionId(id);
  }, []);

  const value = React.useMemo(() => ({ activeJobId, setActiveJobId }), [activeJobId, setActiveJobId]);
  return <RequisitionContext.Provider value={value}>{children}</RequisitionContext.Provider>;
}

export function useActiveRequisition(): Ctx {
  const c = React.useContext(RequisitionContext);
  if (!c) throw new Error("useActiveRequisition must be used within RequisitionProvider");
  return c;
}
