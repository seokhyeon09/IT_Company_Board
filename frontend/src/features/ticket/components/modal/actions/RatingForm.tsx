import React from 'react';
import { Star, Loader2 } from 'lucide-react';

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
  const hasRated = rating && rating !== '0';

  if (needsRating) {
    return (
      <div className="p-4 bg-indigo-50/70 border border-indigo-200 rounded-xl">
        <div className="flex items-center space-x-1.5 mb-2">
          <Star className="w-4 h-4 text-indigo-600 fill-indigo-500" />
          <h4 className="text-xs font-bold text-indigo-900 uppercase tracking-wider">
            조치 만족도 평가 (평가 시 최종 종결)
          </h4>
        </div>
        <form onSubmit={onSubmitRating} className="space-y-3">
          <div className="flex items-center space-x-2">
            <span className="text-xs font-medium text-slate-600">만족도 점수:</span>
            <div className="flex space-x-1">
              {[1, 2, 3, 4, 5].map((score) => (
                <button
                  key={score}
                  type="button"
                  onClick={() => setRatingScore(score)}
                  className="p-1 text-amber-400 hover:scale-110 transition-transform cursor-pointer"
                >
                  <Star
                    className={`w-5 h-5 ${
                      score <= ratingScore ? 'fill-amber-400 text-amber-400' : 'text-slate-300'
                    }`}
                  />
                </button>
              ))}
            </div>
            <span className="text-xs font-bold text-indigo-700 ml-1">{ratingScore}점</span>
          </div>

          <textarea
            value={ratingCommentInput}
            onChange={(e) => setRatingCommentInput(e.target.value)}
            placeholder="처리 과정에 대한 소감이나 의견을 남겨주세요 (선택사항)..."
            rows={2}
            className="w-full text-xs p-2.5 bg-white border border-indigo-200 rounded-lg focus:outline-none focus:ring-2 focus:ring-indigo-400 resize-none"
          />
          {ratingError && (
            <p className="text-xs text-rose-600 font-medium">{ratingError}</p>
          )}
          <div className="flex justify-end">
            <button
              type="submit"
              disabled={submittingRating}
              className="flex items-center px-3.5 py-1.5 text-xs font-semibold text-white bg-indigo-600 hover:bg-indigo-700 rounded-lg shadow-2xs cursor-pointer"
            >
              {submittingRating && <Loader2 className="w-3.5 h-3.5 mr-1.5 animate-spin" />}
              평가 제출 및 문의 종결
            </button>
          </div>
        </form>
      </div>
    );
  }

  if (hasRated) {
    return (
      <div className="p-3 bg-slate-50 border border-slate-200 rounded-xl flex items-center justify-between text-xs">
        <div className="flex items-center space-x-2">
          <span className="font-semibold text-slate-700">사원 만족도 평가:</span>
          <div className="flex text-amber-400">
            {Array.from({ length: Number(rating) || 5 }).map((_, i) => (
              <Star key={i} className="w-4 h-4 fill-amber-400 text-amber-400" />
            ))}
          </div>
          <span className="font-bold text-slate-800">{rating}점</span>
        </div>
        {ratingComment && (
          <span className="text-slate-500 italic max-w-xs truncate" title={ratingComment}>
            &quot;{ratingComment}&quot;
          </span>
        )}
      </div>
    );
  }

  return null;
};
