const builderData = window.BUILDER_DATA || {}
const selectedCatalogCake = window.SELECTED_CATALOG_CAKE || null
const reorderData = window.REORDER_DATA || null

const builderApp = Vue.createApp({
    name: "App",
    components: {
        VForm: VeeValidate.Form,
        VField: VeeValidate.Field,
        ErrorMessage: VeeValidate.ErrorMessage,
    },
    data() {
        return {
            schema1: {
                lvls: (value) => {
                    if (value) {
                        return true;
                    }
                    return ' количество уровней';
                },
                form: (value) => {
                    if (value) {
                        return true;
                    }
                    return ' форму торта';
                },
                topping: (value) => {
                    if (value) {
                        return true;
                    }
                    return ' топпинг';
                }
            },
            schema2: {
                name: (value) => {
                    if (value) {
                        return true;
                    }
                    return ' имя';
                },
                phone: (value) => {
                    if (value) {
                        return true;
                    }
                    return ' телефон';
                },
                name_format: (value) => {
                    const regex = /^[a-zA-Zа-яА-Я]+$/
                    if (!value) {
                        return true;
                    }
                    if ( !regex.test(value)) {

                        return '⚠ Формат имени нарушен';
                    }
                    return true;
                },
                email_format: (value) => {
                    const regex = /^[A-Z0-9._%+-]+@[A-Z0-9.-]+\.[A-Z]{2,4}$/i
                    if (!value) {
                        return true;
                    }
                    if ( !regex.test(value)) {

                        return '⚠ Формат почты нарушен';
                    }
                    return true;
                },
                phone_format:(value) => {
                    const regex = /^((8|\+7)[\- ]?)?(\(?\d{3}\)?[\- ]?)?[\d\- ]{7,10}$/
                    if (!value) {
                        return true;
                    }
                    if ( !regex.test(value)) {

                        return '⚠ Формат телефона нарушен';
                    }
                    return true;
                },
                email: (value) => {
                    if (value) {
                        return true;
                    }
                    return ' почту';
                },
                address: (value) => {
                    if (value) {
                        return true;
                    }
                    return ' адрес';
                },
                date: (value) => {
                    if (value) {
                        return true;
                    }
                    return ' дату доставки';
                },
                time: (value) => {
                    if (value) {
                        return true;
                    }
                    return ' время доставки';
                },
                personal_data_consent: (value) => {
                    if (value) {
                        return true;
                    }
                    return ' согласие на обработку данных';
                }
            },
            DATA: builderData.labels || {
                Levels: {},
                Forms: {},
                Toppings: {},
                Berries: {},
                Decors: {}
            },
            Costs: builderData.costs || {
                Levels: {},
                Forms: {},
                Toppings: {},
                Berries: {},
                Decors: {},
                Words: 500
            },
            Levels: reorderData ? String(reorderData.level || '') : '',
            Form: reorderData ? String(reorderData.shape || '') : '',
            Topping: reorderData ? String(reorderData.topping || '') : '',
            Berries: reorderData ? String(reorderData.berry || '') : '',
            Decor: reorderData ? String(reorderData.decor || '') : '',
            Words: reorderData ? reorderData.inscription || '' : '',
            Comments: reorderData ? reorderData.order_comment || '' : '',
            Designed: Boolean(selectedCatalogCake || reorderData),
            SelectedCatalogCake: selectedCatalogCake,

            Name: reorderData ? reorderData.customer_name || '' : '',
            Phone: reorderData ? reorderData.customer_phone || null : null,
            Email: reorderData ? reorderData.customer_email || null : null,
            Address: reorderData ? reorderData.delivery_address || null : null,
            Dates: null,
            Time: null,
            DelivComments: reorderData ? reorderData.delivery_comment || '' : '',
            PromoCode: '',
            PromoDiscount: 0,
            PromoMessage: '',
            PromoError: false,
            PromoPreviewTimeout: null,
            PersonalDataConsent: false
        }
    },
    mounted() {
        if (this.Designed) {
            this.$nextTick(() => {
                const checkoutSection = document.getElementById('step4')
                if (checkoutSection) {
                    checkoutSection.scrollIntoView({behavior: 'smooth'})
                }
            })
        }
    },
    methods: {
        ToStep4() {
            if (this.Levels && this.Form && this.Topping) {
                this.SelectedCatalogCake = null
            }
            this.Designed = true
            setTimeout(() => this.$refs.ToStep4.click(), 0);
        },
        submitOrder() {
            document.getElementById('order-form').submit()
        },
        schedulePromoPreview() {
            if (this.PromoPreviewTimeout) {
                clearTimeout(this.PromoPreviewTimeout)
            }

            this.PromoPreviewTimeout = setTimeout(() => {
                this.updatePromoPreview()
            }, 300)
        },
        async updatePromoPreview() {
            if (!this.PromoCode) {
                this.PromoDiscount = 0
                this.PromoMessage = ''
                this.PromoError = false
                return
            }

            try {
                const params = new URLSearchParams({
                    promo_code: this.PromoCode,
                    subtotal: String(this.Cost),
                })
                const response = await fetch(`/orders/promo-preview/?${params.toString()}`)
                const data = await response.json()

                if (!response.ok || !data.ok) {
                    this.PromoDiscount = 0
                    this.PromoMessage = data.message || 'Промокод не найден.'
                    this.PromoError = true
                    return
                }

                this.PromoDiscount = Number(data.discount_amount || 0)
                this.PromoMessage = data.message || ''
                this.PromoError = false
            } catch (error) {
                this.PromoDiscount = 0
                this.PromoMessage = 'Не удалось проверить промокод.'
                this.PromoError = true
            }
        },
        getOptionPrice(groupName, optionId) {
            const group = this.Costs[groupName] || {}
            const key = String(optionId || '')
            const price = group[key]

            if (price === undefined || price === null || price === '') {
                return 0
            }

            const normalizedPrice = Number(price)
            return Number.isNaN(normalizedPrice) ? 0 : normalizedPrice
        },
        getDeliveryDateTime() {
            if (!this.Dates || !this.Time) {
                return null
            }

            const deliveryDateTime = new Date(`${this.Dates}T${this.Time}`)
            if (Number.isNaN(deliveryDateTime.getTime())) {
                return null
            }

            return deliveryDateTime
        }
    },
    computed: {
        BaseCost() {
            if (this.SelectedCatalogCake) {
                return Number(this.SelectedCatalogCake.price || 0)
            }

            let inscriptionPrice = this.Words ? this.Costs.Words : 0

            return this.getOptionPrice('Levels', this.Levels) +
                this.getOptionPrice('Forms', this.Form) +
                this.getOptionPrice('Toppings', this.Topping) +
                this.getOptionPrice('Berries', this.Berries) +
                this.getOptionPrice('Decors', this.Decor) +
                Number(inscriptionPrice)
        },
        RushFee() {
            const deliveryDateTime = this.getDeliveryDateTime()
            if (!deliveryDateTime) {
                return 0
            }

            const now = new Date()
            const timeDiff = deliveryDateTime.getTime() - now.getTime()

            if (timeDiff <= 0) {
                return 0
            }

            const hours24 = 24 * 60 * 60 * 1000
            if (timeDiff < hours24) {
                return Math.floor(this.BaseCost * 20 / 100)
            }

            return 0
        },
        Cost() {
            return this.BaseCost + this.RushFee
        },
        FinalCost() {
            return this.Cost - this.PromoDiscount
        }
    },
    watch: {
        PromoCode() {
            this.schedulePromoPreview()
        },
        Cost() {
            if (this.PromoCode) {
                this.updatePromoPreview()
            }
        }
    }
})

builderApp.config.compilerOptions.delimiters = ['[[', ']]']
builderApp.mount('#VueApp')
