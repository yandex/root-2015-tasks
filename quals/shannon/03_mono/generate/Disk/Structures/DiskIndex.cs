#region

using System;

#endregion

namespace Catalogizer.Core {
    public sealed class DiskIndex : IComparable <DiskIndex> {
        public DiskIndex (char letter, byte number) {
            this.Letter = letter;
            this.Number = number;
        }

        public char Letter { get; private set; }

        public byte Number { get; private set; }

        #region IComparable<DiskIndex> Members

        public int CompareTo (DiskIndex other) {
            if ((this.Letter < other.Letter) || (this.Letter == other.Letter && this.Number < other.Number))
                return -1;

            if ((this.Letter > other.Letter) || (this.Letter == other.Letter && this.Number > other.Number))
                return 1;

            return 0;
        }

        #endregion

        public static DiskIndex Parse (string str) {
            if (str == null)
                throw new ArgumentNullException ();

            if (str.Length < 2)
                throw new ArgumentException ();

            return new DiskIndex (str [0], byte.Parse (str.Substring (1)));
        }

        public override string ToString () {
            return string.Format ("{0}{1:D2}", this.Letter.ToString ().ToUpper (), this.Number);
        }
    }
}
