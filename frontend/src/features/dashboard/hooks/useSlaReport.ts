import { useCallback, useEffect, useRef, useState } from 'react';
import { getErrorMessage } from '../../../api/client';
import { reportApi } from '../../../api/reportApi';
import { downloadBlob } from '../../../shared/utils/downloadBlob';
import {
  SlaReportData,
  SlaReportPresetKey,
  SlaReportQueryParams,
  SlaReportUnit,
} from '../types/slaReport';
import { getPresetRange } from '../utils/slaReport';

export function useSlaReport(isOpen: boolean) {
  const [preset, setPreset] = useState<SlaReportPresetKey>('12w');
  const [range, setRange] = useState<{ date_from: string; date_to: string; unit: SlaReportUnit }>(
    () => getPresetRange('12w')
  );
  const [category, setCategory] = useState<string>('');
  const [data, setData] = useState<SlaReportData | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [exporting, setExporting] = useState(false);
  const [exportError, setExportError] = useState<string | null>(null);

  const requestIdRef = useRef(0);

  const selectPreset = useCallback((nextPreset: SlaReportPresetKey) => {
    setPreset(nextPreset);
    setRange(getPresetRange(nextPreset));
  }, []);

  const changeUnit = useCallback((nextUnit: SlaReportUnit) => {
    setRange((prev) => ({ ...prev, unit: nextUnit }));
  }, []);

  const queryParams: SlaReportQueryParams = {
    date_from: range.date_from,
    date_to: range.date_to,
    unit: range.unit,
    category: category || undefined,
  };

  useEffect(() => {
    if (!isOpen) return;

    const currentId = ++requestIdRef.current;
    const controller = new AbortController();

    const fetchReport = async () => {
      setLoading(true);
      setError(null);
      try {
        const res = await reportApi.getSlaReport(
          {
            date_from: range.date_from,
            date_to: range.date_to,
            unit: range.unit,
            category: category || undefined,
          },
          { signal: controller.signal }
        );
        if (requestIdRef.current === currentId) {
          setData(res);
        }
      } catch (err: any) {
        if (controller.signal.aborted || err?.name === 'CanceledError' || err?.code === 'ERR_CANCELED') {
          return;
        }
        if (requestIdRef.current === currentId) {
          setError(getErrorMessage(err, 'SLA 리포트를 불러오지 못했습니다.'));
        }
      } finally {
        if (requestIdRef.current === currentId) {
          setLoading(false);
        }
      }
    };

    fetchReport();
    return () => {
      controller.abort();
    };
  }, [isOpen, range.date_from, range.date_to, range.unit, category]);

  const exportCsv = useCallback(async () => {
    if (exporting) return;
    setExporting(true);
    setExportError(null);
    try {
      const { blob, filename } = await reportApi.exportSlaReport({
        date_from: range.date_from,
        date_to: range.date_to,
        unit: range.unit,
        category: category || undefined,
      });
      downloadBlob(blob, filename);
    } catch (err) {
      setExportError(getErrorMessage(err, 'SLA 리포트 CSV 내보내기에 실패했습니다.'));
    } finally {
      setExporting(false);
    }
  }, [exporting, range.date_from, range.date_to, range.unit, category]);

  return {
    preset,
    unit: range.unit,
    dateFrom: range.date_from,
    dateTo: range.date_to,
    category,
    queryParams,
    data,
    loading,
    error,
    exporting,
    exportError,
    selectPreset,
    changeUnit,
    setCategory,
    exportCsv,
  };
}
