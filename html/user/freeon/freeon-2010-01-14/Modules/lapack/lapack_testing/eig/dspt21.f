      SUBROUTINE DSPT21( ITYPE, UPLO, N, KBAND, AP, D, E, U, LDU, VP,
     $                   TAU, WORK, RESULT )
*
*  -- LAPACK test routine (version 3.1) --
*     Univ. of Tennessee, Univ. of California Berkeley and NAG Ltd..
*     November 2006
*
*     .. Scalar Arguments ..
      CHARACTER          UPLO
      INTEGER            ITYPE, KBAND, LDU, N
*     ..
*     .. Array Arguments ..
      DOUBLE PRECISION   AP( * ), D( * ), E( * ), RESULT( 2 ), TAU( * ),
     $                   U( LDU, * ), VP( * ), WORK( * )
*     ..
*
*  Purpose
*  =======
*
*  DSPT21  generally checks a decomposition of the form
*
*          A = U S U'
*
*  where ' means transpose, A is symmetric (stored in packed format), U
*  is orthogonal, and S is diagonal (if KBAND=0) or symmetric
*  tridiagonal (if KBAND=1).  If ITYPE=1, then U is represented as a
*  dense matrix, otherwise the U is expressed as a product of
*  Householder transformations, whose vectors are stored in the array
*  "V" and whose scaling constants are in "TAU"; we shall use the
*  letter "V" to refer to the product of Householder transformations
*  (which should be equal to U).
*
*  Specifically, if ITYPE=1, then:
*
*          RESULT(1) = | A - U S U' | / ( |A| n ulp ) *and*
*          RESULT(2) = | I - UU' | / ( n ulp )
*
*  If ITYPE=2, then:
*
*          RESULT(1) = | A - V S V' | / ( |A| n ulp )
*
*  If ITYPE=3, then:
*
*          RESULT(1) = | I - VU' | / ( n ulp )
*
*  Packed storage means that, for example, if UPLO='U', then the columns
*  of the upper triangle of A are stored one after another, so that
*  A(1,j+1) immediately follows A(j,j) in the array AP.  Similarly, if
*  UPLO='L', then the columns of the lower triangle of A are stored one
*  after another in AP, so that A(j+1,j+1) immediately follows A(n,j)
*  in the array AP.  This means that A(i,j) is stored in:
*
*     AP( i + j*(j-1)/2 )                 if UPLO='U'
*
*     AP( i + (2*n-j)*(j-1)/2 )           if UPLO='L'
*
*  The array VP bears the same relation to the matrix V that A does to
*  AP.
*
*  For ITYPE > 1, the transformation U is expressed as a product
*  of Householder transformations:
*
*     If UPLO='U', then  V = H(n-1)...H(1),  where
*
*         H(j) = I  -  tau(j) v(j) v(j)'
*
*     and the first j-1 elements of v(j) are stored in V(1:j-1,j+1),
*     (i.e., VP( j*(j+1)/2 + 1 : j*(j+1)/2 + j-1 ) ),
*     the j-th element is 1, and the last n-j elements are 0.
*
*     If UPLO='L', then  V = H(1)...H(n-1),  where
*
*         H(j) = I  -  tau(j) v(j) v(j)'
*
*     and the first j elements of v(j) are 0, the (j+1)-st is 1, and the
*     (j+2)-nd through n-th elements are stored in V(j+2:n,j) (i.e.,
*     in VP( (2*n-j)*(j-1)/2 + j+2 : (2*n-j)*(j-1)/2 + n ) .)
*
*  Arguments
*  =========
*
*  ITYPE   (input) INTEGER
*          Specifies the type of tests to be performed.
*          1: U expressed as a dense orthogonal matrix:
*             RESULT(1) = | A - U S U' | / ( |A| n ulp )   *and*
*             RESULT(2) = | I - UU' | / ( n ulp )
*
*          2: U expressed as a product V of Housholder transformations:
*             RESULT(1) = | A - V S V' | / ( |A| n ulp )
*
*          3: U expressed both as a dense orthogonal matrix and
*             as a product of Housholder transformations:
*             RESULT(1) = | I - VU' | / ( n ulp )
*
*  UPLO    (input) CHARACTER
*          If UPLO='U', AP and VP are considered to contain the upper
*          triangle of A and V.
*          If UPLO='L', AP and VP are considered to contain the lower
*          triangle of A and V.
*
*  N       (input) INTEGER
*          The size of the matrix.  If it is zero, DSPT21 does nothing.
*          It must be at least zero.
*
*  KBAND   (input) INTEGER
*          The bandwidth of the matrix.  It may only be zero or one.
*          If zero, then S is diagonal, and E is not referenced.  If
*          one, then S is symmetric tri-diagonal.
*
*  AP      (input) DOUBLE PRECISION array, dimension (N*(N+1)/2)
*          The original (unfactored) matrix.  It is assumed to be
*          symmetric, and contains the columns of just the upper
*          triangle (UPLO='U') or only the lower triangle (UPLO='L'),
*          packed one after another.
*
*  D       (input) DOUBLE PRECISION array, dimension (N)
*          The diagonal of the (symmetric tri-) diagonal matrix.
*
*  E       (input) DOUBLE PRECISION array, dimension (N-1)
*          The off-diagonal of the (symmetric tri-) diagonal matrix.
*          E(1) is the (1,2) and (2,1) element, E(2) is the (2,3) and
*          (3,2) element, etc.
*          Not referenced if KBAND=0.
*
*  U       (input) DOUBLE PRECISION array, dimension (LDU, N)
*          If ITYPE=1 or 3, this contains the orthogonal matrix in
*          the decomposition, expressed as a dense matrix.  If ITYPE=2,
*          then it is not referenced.
*
*  LDU     (input) INTEGER
*          The leading dimension of U.  LDU must be at least N and
*          at least 1.
*
*  VP      (input) DOUBLE PRECISION array, dimension (N*(N+1)/2)
*          If ITYPE=2 or 3, the columns of this array contain the
*          Householder vectors used to describe the orthogonal matrix
*          in the decomposition, as described in purpose.
*          *NOTE* If ITYPE=2 or 3, V is modified and restored.  The
*          subdiagonal (if UPLO='L') or the superdiagonal (if UPLO='U')
*          is set to one, and later reset to its original value, during
*          the course of the calculation.
*          If ITYPE=1, then it is neither referenced nor modified.
*
*  TAU     (input) DOUBLE PRECISION array, dimension (N)
*          If ITYPE >= 2, then TAU(j) is the scalar factor of
*          v(j) v(j)' in the Householder transformation H(j) of
*          the product  U = H(1)...H(n-2)
*          If ITYPE < 2, then TAU is not referenced.
*
*  WORK    (workspace) DOUBLE PRECISION array, dimension (N**2+N)
*          Workspace.
*
*  RESULT  (output) DOUBLE PRECISION array, dimension (2)
*          The values computed by the two tests described above.  The
*          values are currently limited to 1/ulp, to avoid overflow.
*          RESULT(1) is always modified.  RESULT(2) is modified only
*          if ITYPE=1.
*
*  =====================================================================
*
*     .. Parameters ..
      DOUBLE PRECISION   ZERO, ONE, TEN
      PARAMETER          ( ZERO = 0.0D0, ONE = 1.0D0, TEN = 10.0D0 )
      DOUBLE PRECISION   HALF
      PARAMETER          ( HALF = 1.0D+0 / 2.0D+0 )
*     ..
*     .. Local Scalars ..
      LOGICAL            LOWER
      CHARACTER          CUPLO
      INTEGER            IINFO, J, JP, JP1, JR, LAP
      DOUBLE PRECISION   ANORM, TEMP, ULP, UNFL, VSAVE, WNORM
*     ..
*     .. External Functions ..
      LOGICAL            LSAME
      DOUBLE PRECISION   DDOT, DLAMCH, DLANGE, DLANSP
      EXTERNAL           LSAME, DDOT, DLAMCH, DLANGE, DLANSP
*     ..
*     .. External Subroutines ..
      EXTERNAL           DAXPY, DCOPY, DGEMM, DLACPY, DLASET, DOPMTR,
     $                   DSPMV, DSPR, DSPR2
*     ..
*     .. Intrinsic Functions ..
      INTRINSIC          DBLE, MAX, MIN
*     ..
*     .. Executable Statements ..
*
*     1)      Constants
*
      RESULT( 1 ) = ZERO
      IF( ITYPE.EQ.1 )
     $   RESULT( 2 ) = ZERO
      IF( N.LE.0 )
     $   RETURN
*
      LAP = ( N*( N+1 ) ) / 2
*
      IF( LSAME( UPLO, 'U' ) ) THEN
         LOWER = .FALSE.
         CUPLO = 'U'
      ELSE
         LOWER = .TRUE.
         CUPLO = 'L'
      END IF
*
      UNFL = DLAMCH( 'Safe minimum' )
      ULP = DLAMCH( 'Epsilon' )*DLAMCH( 'Base' )
*
*     Some Error Checks
*
      IF( ITYPE.LT.1 .OR. ITYPE.GT.3 ) THEN
         RESULT( 1 ) = TEN / ULP
         RETURN
      END IF
*
*     Do Test 1
*
*     Norm of A:
*
      IF( ITYPE.EQ.3 ) THEN
         ANORM = ONE
      ELSE
         ANORM = MAX( DLANSP( '1', CUPLO, N, AP, WORK ), UNFL )
      END IF
*
*     Compute error matrix:
*
      IF( ITYPE.EQ.1 ) THEN
*
*        ITYPE=1: error = A - U S U'
*
         CALL DLASET( 'Full', N, N, ZERO, ZERO, WORK, N )
         CALL DCOPY( LAP, AP, 1, WORK, 1 )
*
         DO 10 J = 1, N
            CALL DSPR( CUPLO, N, -D( J ), U( 1, J ), 1, WORK )
   10    CONTINUE
*
         IF( N.GT.1 .AND. KBAND.EQ.1 ) THEN
            DO 20 J = 1, N - 1
               CALL DSPR2( CUPLO, N, -E( J ), U( 1, J ), 1, U( 1, J+1 ),
     $                     1, WORK )
   20       CONTINUE
         END IF
         WNORM = DLANSP( '1', CUPLO, N, WORK, WORK( N**2+1 ) )
*
      ELSE IF( ITYPE.EQ.2 ) THEN
*
*        ITYPE=2: error = V S V' - A
*
         CALL DLASET( 'Full', N, N, ZERO, ZERO, WORK, N )
*
         IF( LOWER ) THEN
            WORK( LAP ) = D( N )
            DO 40 J = N - 1, 1, -1
               JP = ( ( 2*N-J )*( J-1 ) ) / 2
               JP1 = JP + N - J
               IF( KBAND.EQ.1 ) THEN
                  WORK( JP+J+1 ) = ( ONE-TAU( J ) )*E( J )
                  DO 30 JR = J + 2, N
                     WORK( JP+JR ) = -TAU( J )*E( J )*VP( JP+JR )
   30             CONTINUE
               END IF
*
               IF( TAU( J ).NE.ZERO ) THEN
                  VSAVE = VP( JP+J+1 )
                  VP( JP+J+1 ) = ONE
                  CALL DSPMV( 'L', N-J, ONE, WORK( JP1+J+1 ),
     $                        VP( JP+J+1 ), 1, ZERO, WORK( LAP+1 ), 1 )
                  TEMP = -HALF*TAU( J )*DDOT( N-J, WORK( LAP+1 ), 1,
     $                   VP( JP+J+1 ), 1 )
                  CALL DAXPY( N-J, TEMP, VP( JP+J+1 ), 1, WORK( LAP+1 ),
     $                        1 )
                  CALL DSPR2( 'L', N-J, -TAU( J ), VP( JP+J+1 ), 1,
     $                        WORK( LAP+1 ), 1, WORK( JP1+J+1 ) )
                  VP( JP+J+1 ) = VSAVE
               END IF
               WORK( JP+J ) = D( J )
   40       CONTINUE
         ELSE
            WORK( 1 ) = D( 1 )
            DO 60 J = 1, N - 1
               JP = ( J*( J-1 ) ) / 2
               JP1 = JP + J
               IF( KBAND.EQ.1 ) THEN
                  WORK( JP1+J ) = ( ONE-TAU( J ) )*E( J )
                  DO 50 JR = 1, J - 1
                     WORK( JP1+JR ) = -TAU( J )*E( J )*VP( JP1+JR )
   50             CONTINUE
               END IF
*
               IF( TAU( J ).NE.ZERO ) THEN
                  VSAVE = VP( JP1+J )
                  VP( JP1+J ) = ONE
                  CALL DSPMV( 'U', J, ONE, WORK, VP( JP1+1 ), 1, ZERO,
     $                        WORK( LAP+1 ), 1 )
                  TEMP = -HALF*TAU( J )*DDOT( J, WORK( LAP+1 ), 1,
     $                   VP( JP1+1 ), 1 )
                  CALL DAXPY( J, TEMP, VP( JP1+1 ), 1, WORK( LAP+1 ),
     $                        1 )
                  CALL DSPR2( 'U', J, -TAU( J ), VP( JP1+1 ), 1,
     $                        WORK( LAP+1 ), 1, WORK )
                  VP( JP1+J ) = VSAVE
               END IF
               WORK( JP1+J+1 ) = D( J+1 )
   60       CONTINUE
         END IF
*
         DO 70 J = 1, LAP
            WORK( J ) = WORK( J ) - AP( J )
   70    CONTINUE
         WNORM = DLANSP( '1', CUPLO, N, WORK, WORK( LAP+1 ) )
*
      ELSE IF( ITYPE.EQ.3 ) THEN
*
*        ITYPE=3: error = U V' - I
*
         IF( N.LT.2 )
     $      RETURN
         CALL DLACPY( ' ', N, N, U, LDU, WORK, N )
         CALL DOPMTR( 'R', CUPLO, 'T', N, N, VP, TAU, WORK, N,
     $                WORK( N**2+1 ), IINFO )
         IF( IINFO.NE.0 ) THEN
            RESULT( 1 ) = TEN / ULP
            RETURN
         END IF
*
         DO 80 J = 1, N
            WORK( ( N+1 )*( J-1 )+1 ) = WORK( ( N+1 )*( J-1 )+1 ) - ONE
   80    CONTINUE
*
         WNORM = DLANGE( '1', N, N, WORK, N, WORK( N**2+1 ) )
      END IF
*
      IF( ANORM.GT.WNORM ) THEN
         RESULT( 1 ) = ( WNORM / ANORM ) / ( N*ULP )
      ELSE
         IF( ANORM.LT.ONE ) THEN
            RESULT( 1 ) = ( MIN( WNORM, N*ANORM ) / ANORM ) / ( N*ULP )
         ELSE
            RESULT( 1 ) = MIN( WNORM / ANORM, DBLE( N ) ) / ( N*ULP )
         END IF
      END IF
*
*     Do Test 2
*
*     Compute  UU' - I
*
      IF( ITYPE.EQ.1 ) THEN
         CALL DGEMM( 'N', 'C', N, N, N, ONE, U, LDU, U, LDU, ZERO, WORK,
     $               N )
*
         DO 90 J = 1, N
            WORK( ( N+1 )*( J-1 )+1 ) = WORK( ( N+1 )*( J-1 )+1 ) - ONE
   90    CONTINUE
*
         RESULT( 2 ) = MIN( DLANGE( '1', N, N, WORK, N,
     $                 WORK( N**2+1 ) ), DBLE( N ) ) / ( N*ULP )
      END IF
*
      RETURN
*
*     End of DSPT21
*
      END