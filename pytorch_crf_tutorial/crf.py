
import torch
from torch import nn

class CRF(nn.Module):
    """Linear-chain Conditional Random Field (CRF).

    Args:
        nb_labels (int): number of labels in tagset, including special symbols.
        bos_tag_id (int): integer representing beginning of sentence symbol in
                          tagset.
        eos_tag_id (int): integer representing end of sentence symbol tagset.
        batch_first (bool): Whether first dimension represents batch dimension.
    """
    def __init__(self, nb_labels, bos_tag_id, eos_tag_id, batch_first=True):
        super().__init__()
        self.nb_labels = nb_labels
        self.BOS_TAG_ID = bos_tag_id
        self.EOS_TAG_ID = eos_tag_id
        self.batch_first = batch_first
        self.transitions = nn.Parameter(torch.empty(self.nb_labels,
                                                    self.nb_labels))
        self.init_weights()

    def init_weights(self):
        # initialize transitions from a random uniform distribution between
        # -0.1 and 0.1
        nn.init.uniform_(self.transitions, -0.1, 0.1)
        # enforce contraints (rows=from, columns=to) with a big negative number
        # so exp(-10000) will tend to zero
        # no transitions allowed to the beginning of sentence
        self.transitions.data[:, self.BOS_TAG_ID] = -10000.0
        # no transition alloed from the end of sentence
        self.transitions.data[self.EOS_TAG_ID, :] = -10000.0

    def forward(self, emissions, tags, mask=None):
        """Compute the negative log-likelihood. See 'log_likelihood' method."""
        nll = -self.log_likelihood(emissions, tags, mask=mask)
        return nll

    def log_likelihood(self, emissions, tags, mask=None):
        """Compute the probability of a sequence of tags given a sequence of
        emissions scores.

        Args:
            emissions (torch.Tensor): Sequence of emissions for each label.
                Shape of (batch_size, seq_len, nb_labels) if batch_first True,
                (seq_len, batch_size, nb_labels) otherwise.
            tags (torch.LongTensor): Sequence of labels.
                Shape of (batch_size, seq_len) if batch_first is True,
                (seq_len, batch_size) otherwise.
            mask (torch.FloatTensor, optional): Tensor representing valid
                positions.
                If None, all positions are considered valid.
                Shape of (batch_size, seq_len) if batch_first is True,
                (seq_len, batch_size) otherwise.

        Returns:
            torch.Tensor: the log-likelihoods for each sequence in the batch.
                Shape of (batch_size,)
        """

        # fix tensors order by setting batch as the first dimension
        if not self.batch_first:
            emissions = emissions.transpose(0, 1)
            tags = tags.transpose(0, 1)

        if mask is None:
            mask = torch.ones(emissions.shape[:2], dtype=torch.float)

        scores = self._compute_scores(emissions, tags, mask=mask)
        partition = self._compute_log_partition(emissions, mask=mask)
        return torch.sum(scores - partition)

    def _compute_scores(self, emissions, tags, mask):
        """Compute the scores for a given batch of emissions with their tags.

        Args:
            emissions (torch.Tensor): (batch_size, seq_len, nb_labels)
            tags (Torch.LongTensor): (batch_size, seq_len)
            mask (Torch.FloatTensor): (batch_size, seq_len)

        Returns:
            torch.Tensor: Scores for each batch.
                Shape of (batch_size,)
        """
        batch_size, seq_length = tags.shape
        scores = torch.zeros(batch_size)

        # save first and last tags to be used later
        first_tags = tags[:, 0]
        last_valid_idx = mask.int().sum(1) - 1
        last_tags = tags.gather(1, last_valid_idx.unsqueeze(1)).squeeze()

        # add the transition from BOS to the first tags for each batch
        t_scores = self.transitions[self.BOS_TAG_ID, first_tags]

        # add the [unary] emission scores for the first tags for each batch
        # for all batches, the first word, see the correspondent emissions
        # for the first tags (which is a list of ids):
        # emissions[:, 0, [tag_1, tag_2, ..., tag_nblabels]]
        e_scores = emissions[:, 0].gather(1, first_tags.unsqueeze(1)).squeeze()

        # the scores for a word is just the sum of both scores
        scores += e_scores + t_scores

        # now lets do this for each remaining word
        for i in range(1, seq_length):

            # we could: iterate over batches, check if we reached a mask symbol
            # and stop the iteration, but vecotrizing is faster due to gpu,
            # so instead we perform an element-wise multiplication
            is_valid = mask[:, i]

            previous_tags = tags[:, i - 1]
            current_tags = tags[:, i]

            # calculate emission and transition scores as we did before
            e_scores = emissions[:, i].gather(1, current_tags.unsqueeze(1)).squeeze()
            t_scores = self.transitions[previous_tags, current_tags]

            # apply the mask
            e_scores = e_scores * is_valid
            t_scores = t_scores * is_valid

            scores += e_scores + t_scores

        # add the transition from the end tag to the EOS tag for each batch
        scores += self.transitions[last_tags, self.EOS_TAG_ID]

        return scores
