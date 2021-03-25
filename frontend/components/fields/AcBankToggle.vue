<template>
  <ac-bank-toggle-authorize v-if="subject.processor === AUTHORIZE" :value="value" @input="(newValue) => $emit('input', newValue)" :manage-banks="manageBanks" :username="username" />
  <ac-bank-toggle-stripe v-else-if="subject.processor === STRIPE" :value="value" @input="(newValue) => $emit('input', newValue)" :manage-banks="manageBanks" :username="username" />
</template>

<script lang="ts">
import Component, {mixins} from 'vue-class-component'
import {Prop} from 'vue-property-decorator'
import {BANK_STATUSES} from '@/store/profiles/types/BANK_STATUSES'
import {ListController} from '@/store/lists/controller'
import {Bank} from '@/types/Bank'
import {FormController} from '@/store/forms/form-controller'
import AcFormDialog from '@/components/wrappers/AcFormDialog.vue'
import {flatten, genId} from '@/lib/lib'
import Subjective from '@/mixins/subjective'
import AcBoundField from '@/components/fields/AcBoundField'
import AcConfirmation from '@/components/wrappers/AcConfirmation.vue'
import {SingleController} from '@/store/singles/controller'
import {Balance} from '@/types/Balance'
import {PROCESSORS} from '@/types/PROCESSORS'
import AcBankToggleAuthorize from '@/components/fields/AcBankToggleAuthorize.vue'
import AcBankToggleStripe from '@/components/fields/AcBankToggleStripe.vue'

// Will probably never use this again, but can factor it out if I do.
declare type RemoteFlag = {
  value: boolean
}

  @Component({
    components: {AcBankToggleStripe, AcBankToggleAuthorize, AcConfirmation, AcBoundField, AcFormDialog},
  })
export default class AcBankToggle extends mixins(Subjective) {
    @Prop({required: true})
    public value!: BANK_STATUSES

    @Prop({default: false})
    public manageBanks!: boolean

    public AUTHORIZE = PROCESSORS.AUTHORIZE
    public STRIPE = PROCESSORS.STRIPE
}
</script>
