/** @odoo-module **/

export class DateRangeCalculator {
    constructor() {
      this.now = new Date();
    }
  
    getDateRange(option, default_day = 1) {
      const now = this.now;
      const year = now.getFullYear();
  
      switch(option) {
        // Year options
        case 'current_year':
          return [new Date(year, 0, 1), new Date(year, 11, 31, 23, 59, 59, 999)];
        case 'previous_year':
          return [new Date(year - 1, 0, 1), new Date(year - 1, 11, 31, 23, 59, 59, 999)];
        case 'previous_2_year':
          return [new Date(year - 2, 0, 1), new Date(year - 2, 11, 31, 23, 59, 59, 999)];
        case '3_year_ago':
          return [new Date(year - 3, 0, 1), new Date(year - 3, 11, 31, 23, 59, 59, 999)];
        case 'next_year':
          return [new Date(year + 1, 0, 1), new Date(year + 1, 11, 31, 23, 59, 59, 999)];
        case 'current_and_previous_year':
          return [new Date(year - 1, 0, 1), new Date(year, 11, 31, 23, 59, 59, 999)];
        case 'current_and_next_1_year':
          return [new Date(year, 0, 1), new Date(year + 1, 11, 31, 23, 59, 59, 999)];
        case 'current_and_previous_2_year':
          return [new Date(year - 2, 0, 1), new Date(year, 11, 31, 23, 59, 59, 999)];
  
        // Fiscal Year options (ví dụ: bắt đầu từ 1/4 đến 31/3 năm sau)
        case 'current_fiscal_year':
          return this._getFiscalYearRange(year);
        case 'previous_fiscal_year':
          return this._getFiscalYearRange(year - 1);
        case 'previous_2_fiscal_year':
          return this._getFiscalYearRange(year - 2);
        case 'next_fiscal_year':
          return this._getFiscalYearRange(year + 1);
        case 'current_and_previous_fiscal_year':
          return [this._getFiscalYearRange(year - 1)[0], this._getFiscalYearRange(year)[1]];
        case 'current_and_previous_2_fiscal_year':
          return [this._getFiscalYearRange(year - 2)[0], this._getFiscalYearRange(year)[1]];
        case 'current_and_next_fiscal_year':
          return [this._getFiscalYearRange(year)[0], this._getFiscalYearRange(year + 1)[1]];
  
        // Quarter options
        case 'current_quarter':
          return this._getQuarterRange(now);
        case 'previous_quarter':
          return this._getQuarterRange(this._addMonths(now, -3));
        case 'next_quarter':
          return this._getQuarterRange(this._addMonths(now, 3));
        case 'current_and_previous_quarter':
          return [this._getQuarterRange(this._addMonths(now, -3))[0], this._getQuarterRange(now)[1]];
        case 'current_and_next_quarter':
          return [this._getQuarterRange(now)[0], this._getQuarterRange(this._addMonths(now, 3))[1]];
        case 'current_and_next_3_quarter':
          return [this._getQuarterRange(now)[0], this._getQuarterRange(this._addMonths(now, 9))[1]];
  
        // Month options
        case 'this_month':
          return [new Date(year, now.getMonth(), 1), new Date(year, now.getMonth() + 1, 0, 23, 59, 59, 999)];
        case 'last_month': {
          const lastMonthDate = this._addMonths(now, -1);
          return [new Date(lastMonthDate.getFullYear(), lastMonthDate.getMonth(), 1),
                  new Date(lastMonthDate.getFullYear(), lastMonthDate.getMonth() + 1, 0, 23, 59, 59, 999)];
        }
        case 'next_month': {
          const nextMonthDate = this._addMonths(now, 1);
          return [new Date(nextMonthDate.getFullYear(), nextMonthDate.getMonth(), 1),
                  new Date(nextMonthDate.getFullYear(), nextMonthDate.getMonth() + 1, 0, 23, 59, 59, 999)];
        }
        case 'current_and_previous_month': {
          const lastMonthDate = this._addMonths(now, -1);
          return [new Date(lastMonthDate.getFullYear(), lastMonthDate.getMonth(), 1),
                  new Date(year, now.getMonth() + 1, 0, 23, 59, 59, 999)];
        }
        case 'current_and_next_month': {
          const nextMonthDate = this._addMonths(now, 1);
          return [new Date(year, now.getMonth(), 1),
                  new Date(nextMonthDate.getFullYear(), nextMonthDate.getMonth() + 1, 0, 23, 59, 59, 999)];
        }
  
        // Week options (tuần bắt đầu từ Chủ Nhật)
        case 'this_week':
          return this._getWeekRange(now);
        case 'last_week':
          return this._getWeekRange(this._addDays(now, -7));
        case 'next_week':
          return this._getWeekRange(this._addDays(now, 7));
        case 'current_and_previous_week':
          return [this._getWeekRange(this._addDays(now, -7))[0], this._getWeekRange(now)[1]];
        case 'current_and_next_week':
          return [this._getWeekRange(now)[0], this._getWeekRange(this._addDays(now, 7))[1]];
  
        // Day options
        case 'today':
          return [this._startOfDay(now), this._endOfDay(now)];
        case 'yesterday':
          return [this._startOfDay(this._addDays(now, -1)), this._endOfDay(this._addDays(now, -1))];
        case 'tomorrow':
          return [this._startOfDay(this._addDays(now, 1)), this._endOfDay(this._addDays(now, 1))];
        case 'current_and_previous_day':
          return [this._startOfDay(this._addDays(now, -1)), this._endOfDay(now)];
        case 'current_and_next_day':
          return [this._startOfDay(now), this._endOfDay(this._addDays(now, 1))];

        case 'last_n_day': {
            const target = this._addDays(now, -default_day);
            return [this._startOfDay(target), this._endOfDay(target)];
        }
        case 'next_n_day': {
            const target = this._addDays(now, default_day);
            return [this._startOfDay(target), this._endOfDay(target)];
        }

        default:
          return [null, null];
      }
    }
  
    // Fiscal Year: ví dụ từ 01/04/ năm hiện tại đến 31/03 năm sau
    _getFiscalYearRange(year) {
      return [
        new Date(year, 3, 1),                    // 1/4 năm hiện tại
        new Date(year + 1, 2, 31, 23, 59, 59, 999) // 31/3 năm sau
      ];
    }
  
    // Quarter: dựa trên tháng hiện tại
    _getQuarterRange(date) {
      const month = date.getMonth();
      const quarterStartMonth = Math.floor(month / 3) * 3;
      return [
        new Date(date.getFullYear(), quarterStartMonth, 1),
        new Date(date.getFullYear(), quarterStartMonth + 3, 0, 23, 59, 59, 999)
      ];
    }
  
    // Tuần: bắt đầu Chủ Nhật, kết thúc Thứ Bảy
    _getWeekRange(date) {
      const day = date.getDay();
      const start = new Date(date);
      start.setDate(date.getDate() - day);
      start.setHours(0, 0, 0, 0);
  
      const end = new Date(start);
      end.setDate(start.getDate() + 6);
      end.setHours(23, 59, 59, 999);
  
      return [start, end];
    }
  
    _addDays(date, days) {
      const result = new Date(date);
      result.setDate(result.getDate() + days);
      return result;
    }
  
    _addMonths(date, months) {
      const result = new Date(date);
      result.setMonth(result.getMonth() + months);
      return result;
    }
  
    _startOfDay(date) {
      return new Date(date.getFullYear(), date.getMonth(), date.getDate());
    }
  
    _endOfDay(date) {
      return new Date(date.getFullYear(), date.getMonth(), date.getDate(), 23, 59, 59, 999);
    }
}

export const calculator = new DateRangeCalculator();