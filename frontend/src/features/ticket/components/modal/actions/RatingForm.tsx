import React from 'react';
import { Star, CheckCircle2, Loader2 } from 'lucide-react';

interface RatingFormProps {
  isResolved: boolean;
  isAuthor: boolean;
  rating?: string;
  ratingComment?: string;
  ratingScore: number;
  setRatingScore: (val: number) => void;
  ratingCommentInput: string;
  setRatingCommentInput: (val: string) => void;
  submittingRating: boolean;
  ratingError: string;
  onSubmitRating: (e: React.FormEvent) => void;
}

export const RatingForm: React.FC<RatingFormProps> = ({
  isResolved,
  isAuthor,
  rating,
  ratingComment,
  ratingScore,
  setRatingScore,
  ratingCommentInput,
  setRatingCommentInput,
  submittingRating,
  ratingError,
  onSubmitRating,
}) => {
  const needsRating = isResolved && isAuthor && (!rating || rating === '0');
  const hasRated = Boolean(rating && rating !== '0');

  return (
    <>
      {hasRated && (
        <div className="p-4 bg-amber-50/70 border border-amber-200 rounded-xl">
          <div className="flex items-center justify-between mb-2">
            <div className="flex items-center space-x-1.5">
              <span className="text-xs font-bold text-amber-900 uppercase tracking-wider">
                직원 만족도 평가 결과
              </span>
            </div>
            <div className="flex items-center space-x-1">
              {[1, 2, 3, 4, 5].map((starVal) => (
                <Star
                  key={starVal}
                  className={`w-4 h-4 ${
                    starVal <= Number(rating)
                      ? 'text-amber-500 fill-amber-400'
                      : 'text-slate-300'
                  }`}
                />
              ))}
              <span className="text-xs font-black text-amber-900 ml-1.5">
                {rating}점 / 5점
              </span>
            </div>
          </div>
          {ratingComment && (
            <p className="text-xs text-amber-950 mt-1 italic bg-white/70 p-2.5 rounded-lg border border-amber-100">
              &quot;{ratingComment}&quot;
            </p>
          )}
        </div>
      )}

      {needsRating && (
        <div className="p-4 bg-indigo-50/70 border border-indigo-200 rounded-xl">
          <div className="flex items-center space-x-1.5 mb-2">
            <Star className="w-4 h-4 text-indigo-600 fill-indigo-500" />
            <h4 className="text-xs font-bold text-indigo-900 uppercase tracking-wider">
              조치 만족도 평가 (본인 평가 후 종결)
            </h4>
          </div>
          <p className="text-xs text-slate-500 mb-3">
            IT 지원팀의 조치 내용에 대해 만족도를 평가해 주세요. 평가 완료 시 문의가 최종 종결됩니다.
          </p>

          <form onSubmit={onSubmitRating} className="space-y-3">
            <div className="flex items-center space-x-2 bg-white p-2.5 rounded-xl border border-indigo-100 w-fit">
              <span className="text-xs text-slate-600 font-semibold mr-1">별점:</span>
              {[1, 2, 3, 4, 5].map((s) => (
                <button
                  key={s}
                  type="button"
                  onClick={() => setRatingScore(s)}
                  className="p-1 hover:scale-110 transition-transform cursor-pointer"
                >
                  <Star
                    className={`w-5 h-5 ${
                      s <= ratingScore
                        ? 'text-amber-500 fill-amber-400'
                        : 'text-slate-200'
                    }`}
                  />
                </button>
              ))}
              <span className="text-xs font-bold text-amber-600 ml-1">
                {ratingScore}점
              </span>
            </div>

            <textarea
              rows={2}
              value={ratingCommentInput}
              onChange={(e) => setRatingCommentInput(e.target.value)}
              placeholder="처리 과정에 대한 한줄평이나 감사의견을 남겨주세요 (선택사항)"
              className="w-full px-3.5 py-2 text-xs border border-slate-300 rounded-xl bg-white focus:outline-none focus:ring-2 focus:ring-indigo-500 resize-none"
            />

            {ratingError && (
              <div className="text-xs text-rose-600 bg-rose-50 border border-rose-200 p-2.5 rounded-lg">
                {ratingError}
              </div>
            )}

            <div className="flex justify-end">
              <button
                type="submit"
                disabled={submittingRating}
                className="flex items-center px-4 py-2 bg-indigo-600 hover:bg-indigo-700 text-white font-semibold text-xs rounded-xl shadow-md shadow-indigo-600/20 disabled:opacity-50 transition-all cursor-pointer"
              >
                {submittingRating ? (
                  <>
                    <Loader2 className="w-3.5 h-3.5 mr-1.5 animate-spin" />
                    제출 중...
                  </>
                ) : (
                  <>
                    <CheckCircle2 className="w-3.5 h-3.5 mr-1.5" />
                    만족도 제출 및 문의 종결
                  </>
                )}
              </button>
            </div>
          </form>
        </div>
      )}
    </>
  );
};
