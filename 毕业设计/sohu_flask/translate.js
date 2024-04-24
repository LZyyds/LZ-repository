const cyrtpo = require('crypto')
function y(e) {
    return cyrtpo.createHash("md5").update(e).digest()
}
R = (t) => {
    o = 'ydsecret://query/key/B*RGygVywfNBwpmBaZg*WT7SIOUP2T0C9WHMZN39j^DAdaZhAnxvGcCY6VYFwnHl'
    n = 'ydsecret://query/iv/C@lZe2YzHtZ2CYgaXKSVfsb7Y4QWHjITPPZ0nQp87fBeJ!Iv6v^6fvi2WN@bYpJ4'
    a = y(o)
    i = y(n)
    r = cyrtpo.createDecipheriv("aes-128-cbc", a, i);
    let s = r.update(t, "base64", "utf-8");
    return s += r.final("utf-8"), s
}
function j(e) {
    return cyrtpo.createHash("md5").update(e.toString()).digest("hex")
}
function k(e, t) {
    u = "fanyideskweb";
    d = "webfanyi"
    return j(`client=${u}&mysticTime=${e}&product=${d}&key=${t}`)
}
function get_sign() {
    const o = (new Date).getTime();
    sign = k(o, e = "fsdsogkndfokasodnaso")
    return [sign, o]
}



t = 'Z21kD9ZK1ke6ugku2ccWu-MeDWh3z252xRTQv-wZ6jddVo3tJLe7gIXz4PyxGl73nSfLAADyElSjjvrYdCvEP4pfohVVEX1DxoI0yhm36ytQNvu-WLU94qULZQ72aml6ZXphIaOW6LExPxOxZhRNWjZ2nwQ8ffyuNYgu8fm22UdNp6nVHgJPWZsFSuvqFDHBCcVmb4aObjCNX8IKBgMXm4_oweFXgMffwLUp6R6WbmUAdi58LFIF8h6vRYOROFpAKtbplQnDKqE4QrPgn3XME5vyLLebAadqYg9EDuP7svRBSCVNrS5VnvcN6pWX5wuOetK9X4ddlu9czKzTF4uN_DeUZ3MN_nlSQcUkAih8GpR-jd-cPFcSU_J0gIWBVx4CIdvEdpMXr2JA39e5duOSpX_bjIvODVfA2JclSEcBt1boa2Oqdy5MEjMAHTbHVx5sSqvk4YjFbbbAn1rfS-1NGgNgjzff6c7dD-LNh-TKRbDameY15B2U7UcFP-DUbNeUW_WgsdbDxJyb3ePUFKSmjxBhgAXw6bW4U3Gza4-ExEls41BZTbsKHxkGWZlK9H19HDXAzmWoSyofTVZnNgvR26evPlVZcqlvvgUEIZg4r6pXioEDLRzAqKO-i3J-jOasCdJfdEefqfdTmXV34wHrPk9cLbwovXOBW3qFFGi2a3rAUAAXIPkMagHLX-9kHvvx'

console.log(R(t))
