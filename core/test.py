    def post(self, request, *args, **kwargs):
        try:
            order = core_models.Order.objects.get(user=self.request.user, ordered=False)
            order.email = request.data.get('email')
            order.firstname = request.data.get('firstname')
            order.lastname = request.data.get('lastname')
            order.phone_number = request.data.get('phone_number')
            use_default_shipping = request.data.get(
                'use_default_shipping')
            if use_default_shipping:
                print("Using the defualt shipping address")
                address_qs = core_models.Address.objects.filter(
                    user=self.request.user,
                    address_type='S',
                    default=True
                )
                if address_qs.exists():
                    shipping_address = address_qs[0]
                    order.shipping_address = shipping_address
                    order.save()
                else:
                    messages.info(self.request, "No default shipping address available")
                    return redirect('checkout')
            else:
                print("User is entering a new shipping address")
                shipping_address1 = request.data.get('shipping_address')
                shipping_address2 = request.data.get('shipping_address2')
                shipping_country = request.data.get('shipping_country')
                scity = request.data.get('scity')
                sdistrict = request.data.get('sdistrict')
                sstate = request.data.get('sstate')
                shipping_zip = request.data.get('shipping_zip')
                shipping_address = core_models.Address(
                    user=self.request.user,
                    street_address=shipping_address1,
                    apartment_address=shipping_address2,
                    city = scity,
                    district = sdistrict,
                    state = sstate,
                    country=shipping_country,
                    zip=shipping_zip,
                    address_type='S'
                )
                shipping_address.save()

                order.shipping_address = shipping_address
                order.save()

                set_default_shipping = request.data.get(
                    'set_default_shipping')
                if set_default_shipping:
                    shipping_address.default = True
                    shipping_address.save()

            use_default_billing = request.data.get(
                'use_default_billing')
            same_billing_address = request.data.get(
                'same_billing_address')

            if same_billing_address:
                billing_address = shipping_address
                billing_address.pk = None
                billing_address.save()
                billing_address.address_type = 'B'
                billing_address.save()
                order.billing_address = billing_address
                order.save()

            elif use_default_billing:
                print("Using the defualt billing address")
                address_qs = core_models.Address.objects.filter(
                    user=self.request.user,
                    address_type='B',
                    default=True
                )
                if address_qs.exists():
                    billing_address = address_qs[0]
                    order.billing_address = billing_address
                    order.save()
                else:
                    messages.info(
                        self.request, "No default billing address available")
                    return redirect('checkout')
            else:
                print("User is entering a new billing address")
                billing_address1 = request.data.get('billing_address')
                billing_address2 = request.data.get('billing_address2')
                billing_country = request.data.get('billing_country')
                bcity = request.data.get('bcity')
                bdistrict = request.data.get('bdistrict')
                bstate = request.data.get('bstate')
                billing_zip = request.data.get('billing_zip')
                billing_address = core_models.Address(
                    user=self.request.user,
                    street_address=billing_address1,
                    apartment_address=billing_address2,
                    city = bcity,
                    district = bdistrict,
                    state = bstate,
                    country=billing_country,
                    zip=billing_zip,
                    address_type='B'
                )
                billing_address.save()

                order.billing_address = billing_address
                order.save()

                set_default_billing = form.cleaned_data.get(
                    'set_default_billing')
                if set_default_billing:
                    billing_address.default = True
                    billing_address.save()

                else:
                    messages.info(
                        self.request, "Please fill in the required billing address fields")

            payment_option = 'R'

            if payment_option == 'S':
                return redirect('payment', payment_option='stripe')
            elif payment_option == 'P':
                return redirect('payment', payment_option='paypal')
            elif payment_option == 'R':
                return redirect('/payment')
            else:
                messages.warning(
                    self.request, "Invalid payment option selected")
                return redirect('checkout')
        messages.warning(self.request, "some error occured")
        return redirect("checkout")
    except:
        messages.warning(self.request, "You do not haverstjhrh an active order")
        return redirect("order-summary")